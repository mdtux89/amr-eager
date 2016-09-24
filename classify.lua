require 'dp'
require 'optim'
require 'nngraph'
require 'cunn'

model_rels = nil
model_labels = nil
function load_model(model_dir)
  xp = torch.load(model_dir .. "/model_labels.dat")
  model_labels = xp:model()
  model_labels:evaluate()

  xp = torch.load(model_dir .. "/model_rels.dat")
  model_rels = xp:model()
  model_rels:evaluate()

--  xp = torch.load(model_dir .. "/model_t2s.dat")
--  model_t2s = xp:model()
--  model_t2s:evaluate()

--  xp = torch.load(model_dir .. "/model_reentr.dat")
--  model_t2s = xp:model()
--  model_t2s:evaluate()
end

function argmax_mask(v, mask)
  local maxvalue = (torch.min(v) - 1)
  local maxi = 0
  for i=1,v:size(2) do
    if mask[i] == 1 and v[1][i] > maxvalue then
    	maxvalue = v[1][i]
    	maxi = i
    end
  end
  return maxi
end

function argmax(v)
  local maxvalue = torch.max(v)
  for i=1,v:size(2) do
    if v[1][i] == maxvalue then
      return i
    end
  end
end

function  argmin(v)
  local minvalue = torch.min(v)
  for i=1,v:size(2) do
    if v[1][i] == minvalue then
      return i
    end
  end
end

function string:csvline()
        local sep, fields = ",", {}
        local pattern = string.format("([^%s]+)", sep)
        self:gsub(pattern, function(c) fields[#fields+1] = c end)
        return fields
end

function loadInputRels(data, digitsDataLength, wordsDataLength, posDataLength, depsDataLength)
  local wordsDataOffset = digitsDataLength + 1
  local posDataOffset = wordsDataOffset + wordsDataLength
  local depsDataOffset = posDataOffset + posDataLength

  local vals = torch.Tensor(data:csvline())
  local nFeats = vals:size()[1]

  local xa = torch.Tensor(1, digitsDataLength)
  local xb = torch.Tensor(1, wordsDataLength)
  local xc = torch.Tensor(1, posDataLength)
  local xd = torch.Tensor(1, depsDataLength)

  xa[1] = vals[{{1,wordsDataOffset - 1}}]
  xb[1] = vals[{{wordsDataOffset, wordsDataOffset + wordsDataLength - 1}}]
  xc[1] = vals[{{posDataOffset, posDataOffset + posDataLength - 1}}]
  xd[1] = vals[{{depsDataOffset, nFeats}}]
  return {xa,xb,xc,xd}
end

function loadInputGl(data, wordsDataLength, posDataLength)
  local posDataOffset = wordsDataLength + 1

  local vals = torch.Tensor(data:csvline())
  local nFeats = vals:size()[1]

  local xa = torch.Tensor(1, wordsDataLength)
  local xb = torch.Tensor(1, posDataLength)

  xa[1] = vals[{{1,posDataOffset - 1}}]
  xb[1] = vals[{{posDataOffset, nFeats}}]
  return {xa,xb}
end

function loadInputReentr(data, wordsDataLength)

  local vals = torch.Tensor(data:csvline())
  local nFeats = vals:size()[1]

  local xa = torch.Tensor(1, wordsDataLength)

  xa[1] = vals[{{1,nFeats}}]
  return {xa}
end

function predict(inputs, actions)
  -- 68, 12, 4, 6
	data1 = loadInputRels(inputs, 68, 12, 4, 18)--106, 21, 6, 10
	mask = torch.ByteTensor(actions:csvline())

	l1 = data1[1]:size()[2]
	l2 = data1[2]:size()[2]
	l3 = data1[3]:size()[2]
	l4 = data1[4]:size()[2]

	x1 = torch.Tensor(1, l1)
	x2 = torch.Tensor(1, l2)
	x3 = torch.Tensor(1, l3)
	x4 = torch.Tensor(1, l4)

	x1[1] = data1[1][1]
	x2[1] = data1[2][1]
	x3[1] = data1[3][1]
	x4[1] = data1[4][1]

	local out = model_rels:forward({x1, x2, x3, x4})
	y = argmax_mask(out, mask)
	return y

end

function predict_labels(inputs, actions)
  data1 = loadInputRels(inputs, 38, 10, 2, 2)
  mask = torch.ByteTensor(actions:csvline())
  l1 = data1[1]:size()[2]
  l2 = data1[2]:size()[2]
  l3 = data1[3]:size()[2]
  l4 = data1[4]:size()[2]

  x1 = torch.Tensor(1, l1)
  x2 = torch.Tensor(1, l2)
  x3 = torch.Tensor(1, l3)
  x4 = torch.Tensor(1, l4)

  x1[1] = data1[1][1]
  x2[1] = data1[2][1]
  x3[1] = data1[3][1]
  x4[1] = data1[4][1]

  local out = model_labels:forward({x1, x2, x3, x4})
  y = argmax_mask(out, mask)
  return y
end

function predict_gl(inputs)
  data1 = loadInputGl(inputs, 4, 4)--

  l1 = data1[1]:size()[2]
  l2 = data1[2]:size()[2]

  x1 = torch.Tensor(1, l1)
  x2 = torch.Tensor(1, l2)

  x1[1] = data1[1][1]
  x2[1] = data1[2][1]

  local out = model_t2s:forward({x1, x2})
  y = argmax(out)
  return y

end

function predict_reentr(inputs)
  data1 = loadInputReentr(inputs, 3)--

  l1 = data1[1]:size()[2]

  x1 = torch.Tensor(1, l1)

  x1[1] = data1[1][1]

  local out = model_t2s:forward({x1})
  y = argmax(out)
  return y

end
