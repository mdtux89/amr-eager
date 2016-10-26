require 'dp'
require 'nngraph'

function string:split(sep)
        local sep, fields = sep or ":", {}
        local pattern = string.format("([^%s]+)", sep)
        self:gsub(pattern, function(c) fields[#fields+1] = c end)
        y = fields[#fields]
        fields[#fields] = nil
        return {fields, y}
end

function string:csvline()
        local sep, fields = ",", {}
        local pattern = string.format("([^%s]+)", sep)
        self:gsub(pattern, function(c) fields[#fields+1] = c end)
        return torch.Tensor(fields)
end

function loadDataset(dataFileTrain, dataFileValid, nclasses, digitsDataLength, wordsDataLength, posDataLength, depsDataLength)
  wordsDataOffset = digitsDataLength + 1
  posDataOffset = wordsDataOffset + wordsDataLength
  depsDataOffset = posDataOffset + posDataLength

  cls = {}
  for i=1,nclasses do
    table.insert(cls, i)
  end

  print("Loading training data..")

  local dataSize = 0
  local nFeats = 0
  for line in io.lines(dataFileTrain) do
      dataSize = dataSize + 1
    if nFeats == 0 then
      fields = line:split(",")
      nFeats = #fields[1]
    end
  end

  local xa = torch.Tensor(dataSize, digitsDataLength)
  local xb = torch.Tensor(dataSize, wordsDataLength)
  local xc = torch.Tensor(dataSize, posDataLength)
  local xd = torch.Tensor(dataSize, depsDataLength)
  local y = torch.Tensor(dataSize)

  i = 1
  for line in io.lines(dataFileTrain) do
      fields = line:split(",")
      y[i] = fields[2]
      inp = torch.Tensor(fields[1])
      xa[i] = inp[{{1,wordsDataOffset - 1}}]
      xb[i] = inp[{{wordsDataOffset, wordsDataOffset + wordsDataLength - 1}}]
      xc[i] = inp[{{posDataOffset, posDataOffset + posDataLength - 1}}]
      xd[i] = inp[{{depsDataOffset, nFeats}}]
      i = i + 1
  end
  local trainInput = dp.ListView({dp.DataView('bf', xa), dp.DataView('bf', xb), dp.DataView('bf', xc), dp.DataView('bf', xd)})
  local trainTarget = dp.ClassView('b', y)

  print("Loading dev data..")
  local dataSize = 0
  local nFeats = 0
  for line in io.lines(dataFileValid) do
      dataSize = dataSize + 1
    if nFeats == 0 then
      fields = line:split(",")
      nFeats = #fields[1]
    end
  end

  local xa = torch.Tensor(dataSize, digitsDataLength)
  local xb = torch.Tensor(dataSize, wordsDataLength)
  local xc = torch.Tensor(dataSize, posDataLength)
  local xd = torch.Tensor(dataSize, depsDataLength)
  local y = torch.Tensor(dataSize)

  i = 1
  for line in io.lines(dataFileValid) do
      fields = line:split(",")
      y[i] = fields[2]
      inp = torch.Tensor(fields[1])
      xa[i] = inp[{{1,wordsDataOffset - 1}}]
      xb[i] = inp[{{wordsDataOffset, wordsDataOffset + wordsDataLength - 1}}]
      xc[i] = inp[{{posDataOffset, posDataOffset + posDataLength - 1}}]
      xd[i] = inp[{{depsDataOffset, nFeats}}]
      i = i + 1
  end
  local validInput = dp.ListView({dp.DataView('bf', xa), dp.DataView('bf', xb), dp.DataView('bf', xc), dp.DataView('bf', xd)})
  local validTarget = dp.ClassView('b', y)

  trainTarget:setClasses(cls)
  validTarget:setClasses(cls)
  local train = dp.DataSet{inputs=trainInput,targets=trainTarget,which_set='train'}
  local valid = dp.DataSet{inputs=validInput,targets=validTarget,which_set='valid'}

  local ds = dp.DataSource{train_set=train,valid_set=valid}
  function ds:classes() return cls end
  function ds:featureSize() return nFeats end
  return ds
end

function loadExperiment(opt, dictSizeWords, dictSizePos, dictSizeDeps, outputSize, digitsDataLength, wordsDataLength, posDataLength, depsDataLength)

        inputSize = digitsDataLength + (wordsDataLength * opt.inputEmbeddingSizeWords) + (posDataLength * opt.inputEmbeddingSizePos) + (depsDataLength * opt.inputEmbeddingSizeDeps)
        local inputs = {}
        table.insert(inputs, nn.Identity()())
        table.insert(inputs, nn.Identity()())
        table.insert(inputs, nn.Identity()())
        table.insert(inputs, nn.Identity()())
        paralltab = nn.ParallelTable()

	      digits = nn.Sequential()
        digits:add(nn.Identity())

        --Lookup table for dependency labels
        deps = nn.Sequential()
        depsdict = nn.LookupTable(dictSizeDeps, opt.inputEmbeddingSizeDeps)
        deps:add(depsdict)
        deps:add(nn.Collapse(2))

        --Lookup table for POS tags
        pos = nn.Sequential()
        posdict = nn.LookupTable(dictSizePos, opt.inputEmbeddingSizePos)
        i = 1
        for line in io.lines("resources/posembs.txt") do
          vals = line:csvline()
          posdict.weight[i] = vals
          i = i + 1
        end
        pos:add(posdict)
        pos:add(nn.Collapse(2))

        --Lookup table for words
        words = nn.Sequential()
        wordsdict = nn.LookupTable(dictSizeWords, opt.inputEmbeddingSizeWords)
        i = 1
        for line in io.lines("resources/wordembs.txt") do
          vals = line:csvline()
          wordsdict.weight[i] = vals
          i = i + 1
        end
        words:add(wordsdict)
        words:add(nn.Collapse(2))

        paralltab:add(digits)
        paralltab:add(words)
        paralltab:add(pos)
        paralltab:add(deps)
        embs = paralltab({inputs[1],inputs[2],inputs[3],inputs[4]})
        model = nn.JoinTable(2)(embs)

        for i,hiddenSize in ipairs(opt.hiddenSize) do
          model = nn.Linear(inputSize, hiddenSize)(model)
          if opt.batchNorm then
             model = nn.BatchNormalization(hiddenSize)(model)
          end
          model = nn[opt.activation]()(model)
          if opt.dropout then
             model = nn.Dropout()(model)
          end
          inputSize = hiddenSize
        end

        --output layer
        model = nn.Linear(inputSize, outputSize)(model)
        model = nn.LogSoftMax()(model)
        outputs = {}
        table.insert(outputs, model)
        layer = nn.gModule(inputs, outputs)
        model = nn.Sequential()
        model:add(layer)

        --[[Propagators]]--
        if opt.lrDecay == 'adaptive' then
           ad = dp.AdaptiveDecay{max_wait = opt.maxWait, decay_factor=opt.decayFactor}
        elseif opt.lrDecay == 'linear' then
           opt.decayFactor = (opt.minLR - opt.learningRate)/opt.saturateEpoch
        end

        train = dp.Optimizer{
           acc_update = opt.accUpdate,
           loss = nn.ModuleCriterion(nn.ClassNLLCriterion(), nil, nn.Convert()),
           epoch_callback = function(model, report) -- called every epoch
              -- learning rate decay
              if report.epoch > 0 then
                 if opt.lrDecay == 'adaptive' then
                    opt.learningRate = opt.learningRate*ad.decay
                    ad.decay = 1
                 elseif opt.lrDecay == 'schedule' and opt.schedule[report.epoch] then
                    opt.learningRate = opt.schedule[report.epoch]
                 elseif opt.lrDecay == 'linear' then
                    opt.learningRate = opt.learningRate + opt.decayFactor
                 end
                 opt.learningRate = math.max(opt.minLR, opt.learningRate)
                 if not opt.silent then
			 print("learningRate", opt.learningRate)
                 end
              end
           end,
           callback = function(model, report) -- called for every batch
              if opt.accUpdate then
                 model:accUpdateGradParameters(model.dpnn_input, model.output, opt.learningRate)
              else
                 model:updateGradParameters(opt.momentum) -- affects gradParams
                 model:updateParameters(opt.learningRate) -- affects params
              end
              model:maxParamNorm(opt.maxOutNorm) -- affects params
              model:zeroGradParameters() -- affects gradParams
           end,
           feedback = dp.Confusion(),
           sampler = dp.ShuffleSampler{batch_size = opt.batchSize},
           progress = opt.progress
        }
        valid = dp.Evaluator{
           feedback = dp.Confusion(),
           sampler = dp.Sampler{batch_size = opt.batchSize}
        }
        test = dp.Evaluator{
           feedback = dp.Confusion(),
           sampler = dp.Sampler{batch_size = opt.batchSize}
        }

        --[[Experiment]]--

        xp = dp.Experiment{
           model = model,
           optimizer = train,
           validator = valid,
           -- tester = test,
           observer = {
              dp.FileLogger(),
              dp.EarlyStopper{
                 error_report = {'validator','feedback','confusion','accuracy'},
                 maximize = true,
                 max_epochs = opt.maxTries
              },
              ad
           },
           random_seed = os.time(),
           max_epoch = opt.maxEpoch
        }

        --[[GPU or CPU]]--

        if opt.cuda then
           require 'cutorch'
           require 'cunn'
           cutorch.setDevice(opt.useDevice)
           xp:cuda()
        end

        xp:verbose(not opt.silent)
        if not opt.silent then
           print"Model :"
           print(model)
        end
        return xp
end

cmd = torch.CmdLine()
cmd:text()
cmd:text('Options:')
cmd:option('--learningRate', 0.1, 'learning rate at t=0')
cmd:option('--lrDecay', 'linear', 'type of learning rate decay : adaptive | linear | schedule | none')
cmd:option('--minLR', 0.00001, 'minimum learning rate')
cmd:option('--saturateEpoch', 300, 'epoch at which linear decayed LR will reach minLR')
cmd:option('--schedule', '{}', 'learning rate schedule')
cmd:option('--maxWait', 4, 'maximum number of epochs to wait for a new minima to be found. After that, the learning rate is decayed by decayFactor.')
cmd:option('--decayFactor', 0.001, 'factor by which learning rate is decayed for adaptive decay.')
cmd:option('--maxOutNorm', 2, 'max norm each layers output neuron weights')
cmd:option('--momentum', 0, 'momentum')
cmd:option('--activation', 'Tanh', 'transfer function like ReLU, Tanh, Sigmoid')
cmd:option('--hiddenSize', '{200,200}', 'number of hidden units per layer')
cmd:option('--batchSize', 32, 'number of examples per batch')
cmd:option('--cuda', false, 'use CUDA')
cmd:option('--useDevice', 2, 'sets the device (GPU) to use')
cmd:option('--maxEpoch', 200, 'maximum number of epochs to run')
cmd:option('--maxTries', 30, 'maximum number of epochs to try to find a better local minima for early-stopping')
cmd:option('--dropout', false, 'apply dropout on hidden neurons')
cmd:option('--batchNorm', false, 'use batch normalization. dropout is mostly redundant with this')
cmd:option('--progress', false, 'display progress bar')
cmd:option('--silent', false, 'dont print anything to stdout')
cmd:option('--accUpdate', false, 'accumulate updates inplace using accUpdateGradParameters')
cmd:option('--inputEmbeddingSizeWords', 50, 'embedding size')
cmd:option('--inputEmbeddingSizePos', 10, 'embedding size')
cmd:option('--inputEmbeddingSizeDeps', 10, 'embedding size')
cmd:option('--model_dir', 'LDC2015E86', 'output directory')
cmd:text()

opt = cmd:parse(arg or {})
opt.schedule = dp.returnString(opt.schedule)
opt.hiddenSize = dp.returnString(opt.hiddenSize)
if not opt.silent then
   table.print(opt)
end

local nRels = 0
for line in io.lines(opt.model_dir .. "/relations.txt") do
    nRels = nRels + 1
end
nRels = nRels + 3

local nDeps = 0
for line in io.lines(opt.model_dir .. "/dependencies.txt") do
    nDeps = nDeps + 1
end
nDeps = nDeps + 3

train = opt.model_dir .. "/labels_dataset_train.txt"
valid = opt.model_dir .. "/labels_dataset_valid.txt"
dataset = loadDataset(train, valid, nRels - 3, 40, 10, 2, 2)

xp = loadExperiment(opt, 149507, 52, nDeps, nRels - 3, 40, 10, 2, 2)
xp:run(dataset)
