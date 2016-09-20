require 'rnn'
require 'cutorch'
require 'cunn'
require 'optim'
require 'io'
require 'nngraph'
cutorch.setDevice(1)

function argmax(v)
  local maxvalue = torch.max(v)
  for i=1,v:size()[1] do
    if v[i] == maxvalue then
      return i
    end
  end
end

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

---loadDataset
function loadDataset(dataFile, outputSize, wordsDataLength, posDataLength, nesDataLength, depsDataLength)
  posDataOffset = 1 + wordsDataLength
  nesDataOffset = posDataOffset + posDataLength
  depsDataOffset = nesDataOffset + nesDataLength

  print("Loading data..")
  local dataSize = 0
  local nFeats = 0
  for line in io.lines(dataFile) do
      dataSize = dataSize + 1
    if nFeats == 0 then
      fields = line:split(",")
      nFeats = #fields[1] 
    end
  end

  cls = {}
  for i=1,outputSize do
    table.insert(cls, i)
  end

  local xa = torch.CudaTensor(dataSize, wordsDataLength)
  local xb = torch.CudaTensor(dataSize, posDataLength)
  local xc = torch.CudaTensor(dataSize, nesDataLength)
  local xd = torch.CudaTensor(dataSize, depsDataLength)

  local y = torch.CudaTensor(dataSize)
  i = 1
  for line in io.lines(dataFile) do
      fields = line:split(",")
      y[i] = fields[2]
      inp = torch.CudaTensor(fields[1])
      xa[i] = inp[{{1, wordsDataLength}}]
      xb[i] = inp[{{posDataOffset, posDataOffset + posDataLength - 1}}]
      xc[i] = inp[{{nesDataOffset, nesDataOffset + nesDataLength - 1}}]
      xd[i] = inp[{{depsDataOffset, nFeats}}]
      i = i + 1
  end
  
  local nTrain = math.floor(dataSize*0.8)
  local nValid = math.floor((dataSize - nTrain)/ 2)
  local nTest = dataSize - nTrain - nValid

  local trainInput = {xa[{{1,nTrain}}], xb[{{1,nTrain}}], xc[{{1,nTrain}}], xd[{{1,nTrain}}]]}
  local validInput = {xa[{{nTrain + 1, nTrain + 1 + nValid}}], xb[{{nTrain + 1, nTrain + 1 + nValid}}], xc[{{nTrain + 1, nTrain + 1 + nValid}}], xd[{{nTrain + 1, nTrain + 1 + nValid}}]]}
  local testInput = {xa[{{nTrain + nValid + 2, dataSize}}], xb[{{nTrain + nValid + 2, dataSize}}], xc[{{nTrain + nValid + 2, dataSize}}], xd[{{nTrain + nValid + 2, dataSize}}]]}
  local trainTarget = y[{{1,nTrain}}]
  local validTarget = y[{{nTrain + 1, nTrain + 1 + nValid}}]
  local testTarget = y[{{nTrain + nValid + 2, dataSize}}]
  
  return {trainInput, trainTarget, validInput, validTarget, testInput, testTarget}

end

function loadExperiment(outputSize, wordsDataLength, posDataLength, nesDataLength, depsDataLength)
  --batchSize = 8
  local nRels = 0
  for line in io.lines("resources/relations.txt") do
      nRels = nRels + 1
  end
  nRels = nRels + 3

  local nDeps = 0
  for line in io.lines("resources/dependencies.txt") do
      nDeps = nDeps + 1
  end
  nDeps = nDeps + 3

  local nConcepts = 0
  for line in io.lines("resources/shifts.txt") do
      nConcepts = nConcepts + 1
  end
  nConcepts = nConcepts + 3

  nPos = 52
  nWords = 149507
  nNes = 20

  lr = 0.2

  -- lstm = nn.FastLSTM(opt.lstmhiddenSize, opt.lstmhiddenSize)
  -- fwd = nn.Sequencer(lstm)
  -- bwd = fwd:clone()
  -- bwd:reset()
  -- bwd:remember('neither')

  -- fwd2 = nn.Sequencer(nn.FastLSTM(2 * hiddenSize, hiddenSize):maskZero(1))
  -- bwd2 = fwd:clone()
  -- bwd2:reset()
  -- bwd2:remember('neither')
  -- brnn2 = nn.BiSequencerLM(fwd2, bwd2)

  local inputs = {}
  table.insert(inputs, nn.Identity()())
  table.insert(inputs, nn.Identity()())
  table.insert(inputs, nn.Identity()())
  table.insert(inputs, nn.Identity()())
  paralltab = nn.ParallelTable()

  nes = nn.Sequential()
  nesdict = nn.LookupTable(nNes, opt.inputEmbeddingSizeNes)
  i = 1
  for line in io.lines("resources/nesembs.txt") do
    vals = line:csvline()
    nesdict.weight[i] = vals
    i = i + 1
  end
  nes:add(nesdict)
  nes:add(nn.SplitTable(1,2))
  lstm = nn.FastLSTM(opt.inputEmbeddingSizeNes, opt.lstmhiddenSize)
  fwd = nn.Sequencer(lstm)
  bwd = fwd:clone()
  bwd:reset()
  bwd:remember('neither')
  nes:add(nn.BiSequencerLM(fwd, bwd))
  nes:add(nn.JoinTable(2))
  -- nes:add(nn.Collapse(2))

  -- concepts = nn.Sequential()
  -- conceptdict = nn.LookupTable(nConcepts, opt.inputEmbeddingSizeConcepts)
  -- concepts:add(conceptdict)
  -- concepts:add(nn.SplitTable(1,2))
  -- lstm = nn.FastLSTM(opt.inputEmbeddingSizeConcepts, opt.lstmhiddenSize)
  -- fwd = nn.Sequencer(lstm)
  -- bwd = fwd:clone()
  -- bwd:reset()
  -- bwd:remember('neither')
  -- concepts:add(nn.BiSequencerLM(fwd, bwd))
  -- concepts:add(nn.JoinTable(2))

  deps = nn.Sequential()
  depsdict = nn.LookupTable(nDeps, opt.inputEmbeddingSizeDeps)
  deps:add(depsdict)
  deps:add(nn.SplitTable(1,2))
  lstm = nn.FastLSTM(opt.inputEmbeddingSizeDeps, opt.lstmhiddenSize)
  fwd = nn.Sequencer(lstm)
  bwd = fwd:clone()
  bwd:reset()
  bwd:remember('neither')
  deps:add(nn.BiSequencerLM(fwd, bwd))
  deps:add(nn.JoinTable(2))
  -- deps:add(nn.Collapse(2))

  pos = nn.Sequential()
  posdict = nn.LookupTable(nPos, opt.inputEmbeddingSizePos)
  i = 1
  for line in io.lines("resources/posembs.txt") do
    vals = line:csvline()
    posdict.weight[i] = vals
    i = i + 1
  end
  pos:add(posdict)
  pos:add(nn.SplitTable(1,2))
  lstm = nn.FastLSTM(opt.inputEmbeddingSizePos, opt.lstmhiddenSize)
  fwd = nn.Sequencer(lstm)
  bwd = fwd:clone()
  bwd:reset()
  bwd:remember('neither')
  pos:add(nn.BiSequencerLM(fwd, bwd))
  pos:add(nn.JoinTable(2))
  -- pos:add(nn.Collapse(2))

  words = nn.Sequential()
  wordsdict = nn.LookupTable(nWords, opt.inputEmbeddingSizeWords)
  i = 1
  for line in io.lines("resources/wordembs.txt") do
    vals = line:csvline()
    wordsdict.weight[i] = vals
    i = i + 1
  end
  words:add(wordsdict)
  words:add(nn.SplitTable(1,2))
  lstm = nn.FastLSTM(opt.inputEmbeddingSizeWords, opt.lstmhiddenSize)
  fwd = nn.Sequencer(lstm)
  bwd = fwd:clone()
  bwd:reset()
  bwd:remember('neither')
  words:add(nn.BiSequencerLM(fwd, bwd))
  words:add(nn.JoinTable(2))
  -- words:add(nn.Collapse(2))

  -- paralltab:add(concepts)
  paralltab:add(words)
  paralltab:add(pos)
  paralltab:add(nes)
  paralltab:add(deps)
  embs = paralltab({inputs[1],inputs[2],inputs[3],inputs[4]})

  model = nn.JoinTable(2)(embs)

  outlstmsize = opt.lstmhiddenSize * 2
  inputSize = outlstmsize *  wordsDataLength + outlstmsize * posDataLength + outlstmsize * nesDataLength + outlstmsize * depsDataLength
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

  model:cuda()
  print(model)
  return model
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
cmd:option('--lstmhiddenSize', '200', 'number of hidden units per layer')
cmd:option('--batchSize', 32, 'number of examples per batch')
cmd:option('--cuda', true, 'use CUDA')
cmd:option('--useDevice', 2, 'sets the device (GPU) to use')
cmd:option('--maxEpoch', 200, 'maximum number of epochs to run')
cmd:option('--maxTries', 30, 'maximum number of epochs to try to find a better local minima for early-stopping')
cmd:option('--dropout', true, 'apply dropout on hidden neurons')
cmd:option('--batchNorm', false, 'use batch normalization. dropout is mostly redundant with this')
cmd:option('--progress', false, 'display progress bar')
cmd:option('--silent', false, 'dont print anything to stdout')
cmd:option('--accUpdate', false, 'accumulate updates inplace using accUpdateGradParameters')
cmd:option('--inputEmbeddingSizeConcepts', 25, 'embedding size')
cmd:option('--inputEmbeddingSizeWords', 50, 'embedding size')
cmd:option('--inputEmbeddingSizePos', 10, 'embedding size')
cmd:option('--inputEmbeddingSizeDeps', 10, 'embedding size')
cmd:option('--inputEmbeddingSizeRels', 10, 'embedding size')
cmd:option('--inputEmbeddingSizeNes', 10, 'embedding size')
cmd:text()

opt = cmd:parse(arg or {})

str = "tab = " .. opt.hiddenSize
a = loadstring(str)
a()
opt.hiddenSize = tab


-- criterion = nn.SequencerCriterion(nn.ClassNLLCriterion())
criterion = nn.ClassNLLCriterion()
criterion:cuda()

data = loadDataset("/disk/scratch/s1333293/bidir_dataset.txt", 4, 6, 6, 6, 8)
-- data = loadDataset("bidir_test.txt", 4, 6, 6, 6, 8)
--data is {trainInput, trainTarget, validInput, validTarget, testInput, testTarget}

model = loadExperiment(4, 6, 6, 6, 8)
model:cuda()

-------------------------------------------------------------------------------------
-- Training --
-------------------------------------------------------------------------------------
torch.manualSeed(0)
print("Training..")
best = 0
patience = 10
for iteration = 1, 1000 do
  local inputs, targets = {}, {}
	ds = {}
	ds.size = data[1][1]:size()[1]
	ds.input = data[1]
	ds.target = data[2]
  for t = 1,ds.size,opt.batchSize do
    xlua.progress(t, ds.size)
    --t = torch.random(1, batches) * batchSize - 1
    inputs[1] = ds.input[1][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
    inputs[2] = ds.input[2][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
    inputs[3] = ds.input[3][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
    inputs[4] = ds.input[4][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
    targets[1] = ds.target[{{t,math.min(t+opt.batchSize-1,ds.size)}}]
    -- targets[1] = nn.SplitTable(1, 1):forward(targets[1])

    -- feed it to the neural network and the criterion
    criterion:forward(model:forward(inputs), targets[1])

    -- train over this example in 3 steps
    -- (1) zero the accumulation of the gradients
    model:zeroGradParameters()
    -- (2) accumulate gradients
    model:backward(inputs, criterion:backward(model.output, targets[1]))
    -- (3) update parameters with a 0.01 learning rate
    model:updateParameters(0.01)

--     model:zeroGradParameters() 
--     model:forget()
--     -- lstm:recycle()

--     local outputs = model:forward(inputs)

--     local err = criterion:forward(outputs, targets)
--     -- print(string.format("Iteration %d ; NLL err = %f ", iteration, err))
--     -- print(string.format("Iteration %d ; NLL err = %f ", iteration, err))

--     -- 3. backward sequence through rnn (i.e. backprop through time)
--     local gradOutputs = criterion:backward(outputs, targets)
--     local gradInputs = model:backward(inputs, gradOutputs)
    
--     -- 4. update  
--     model:updateParameters(lr)

-- --       -- break
-- --       -- model:zeroGradParameters()
         
  end
  local err = criterion:forward(model:forward(inputs), targets[1])
  print(string.format("Iteration %d ; NLL err = %f ", iteration, err))

  dsdev = {}
  dsdev.size = data[3][1]:size()[1]
  dsdev.input = data[3]
  dsdev.target = data[4]
  c = 0
  tot = 0
  for t = 1,dsdev.size,opt.batchSize do
    inputs = {}
    inputs[1] = dsdev.input[1][{{t,math.min(t+opt.batchSize-1,dsdev.size)}}]
    inputs[2] = dsdev.input[2][{{t,math.min(t+opt.batchSize-1,dsdev.size)}}]
    inputs[3] = dsdev.input[3][{{t,math.min(t+opt.batchSize-1,dsdev.size)}}]
    inputs[4] = dsdev.input[4][{{t,math.min(t+opt.batchSize-1,dsdev.size)}}]
    targets = dsdev.target[{{t,math.min(t+opt.batchSize-1,dsdev.size)}}]
    local outputs = model:forward(inputs)
    for ex = 1, outputs:size()[1] do
      pred = argmax(outputs[ex])
      if pred == targets[ex] then
        c = c + 1
      end
      tot = tot + 1
    end
  end
  print("Development set accuracy: " .. c/tot*100 .. " %")

  if best < c/tot then
    best = c/tot
    patience = 10
  else
    patience = patience - 1
  end
  if best ~= 0 and patience == 0 then
   break
  end
end

-------------------------------------------------------------------------------------
-- Testing --
-------------------------------------------------------------------------------------

ds = {}
ds.size = data[1][1]:size()[1]
ds.input = data[1]
ds.target = data[2]
c = 0
tot = 0
for t = 1,ds.size,opt.batchSize do
  inputs = {}
  inputs[1] = ds.input[1][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[2] = ds.input[2][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[3] = ds.input[3][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[4] = ds.input[4][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  targets = ds.target[{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  local outputs = model:forward(inputs)
  for ex = 1, outputs:size()[1] do
    pred = argmax(outputs[ex])
    if pred == targets[ex] then
      c = c + 1
    end
    tot = tot + 1
  end
end
print("Training set accuracy: " .. c/tot*100 .. " %")

ds = {}
ds.size = data[3][1]:size()[1]
ds.input = data[3]
ds.target = data[4]
c = 0
tot = 0
for t = 1,ds.size,opt.batchSize do
  inputs = {}
  inputs[1] = ds.input[1][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[2] = ds.input[2][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[3] = ds.input[3][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[4] = ds.input[4][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  targets = ds.target[{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  local outputs = model:forward(inputs)
  for ex = 1, outputs:size()[1] do
    pred = argmax(outputs[ex])
    if pred == targets[ex] then
      c = c + 1
    end
    tot = tot + 1
  end
end
print("Development set accuracy: " .. c/tot*100 .. " %")

ds = {}
ds.size = data[5][1]:size()[1]
ds.input = data[5]
ds.target = data[6]
c = 0
tot = 0
for t = 1,ds.size,opt.batchSize do
  inputs = {}
  inputs[1] = ds.input[1][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[2] = ds.input[2][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[3] = ds.input[3][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  inputs[4] = ds.input[4][{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  targets = ds.target[{{t,math.min(t+opt.batchSize-1,ds.size)}}]
  local outputs = model:forward(inputs)
  for ex = 1, outputs:size()[1] do
    pred = argmax(outputs[ex])
    if pred == targets[ex] then
      c = c + 1
    end
    tot = tot + 1
  end
end
print("Testing set accuracy: " .. c/tot*100 .. " %")
