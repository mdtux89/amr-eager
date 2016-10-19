require 'dp'
require 'optim'
require 'nngraph'
require 'cunn'

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

local Classify = torch.class('Classify')

function Classify:__init(model_dir)
  xp = torch.load(model_dir .. "/labels.dat")
  model_labels = xp:model()
  model_labels:evaluate()

  xp = torch.load(model_dir .. "/actions.dat")
  model_rels = xp:model()
  model_rels:evaluate()

  xp = torch.load(model_dir .. "/reentrancies.dat")
  model_reentr = xp:model()
  model_reentr:evaluate()
end

function Classify:action(digits, words, pos, deps, constr)
  xa = torch.Tensor(1, digits:size()[1])
  xb = torch.Tensor(1, words:size()[1])
  xc = torch.Tensor(1, pos:size()[1])
  xd = torch.Tensor(1, deps:size()[1])
  xa[1] = digits
  xb[1] = words
  xc[1] = pos
  xd[1] = deps
	local out = model_rels:forward({xa, xb, xc, xd})
	y = argmax_mask(out, constr)
	return y
end

function Classify:label(digits, words, pos, deps, constr)
  xa = torch.Tensor(1, digits:size()[1])
  xb = torch.Tensor(1, words:size()[1])
  xc = torch.Tensor(1, pos:size()[1])
  xd = torch.Tensor(1, deps:size()[1])
  xa[1] = digits
  xb[1] = words
  xc[1] = pos
  xd[1] = deps
  local out = model_labels:forward({xa, xb, xc, xd})
  y = argmax_mask(out, constr)
  return y
end

function Classify:reentrancy(words, pos, deps)
  xa = torch.Tensor(1, words:size()[1])
  xb = torch.Tensor(1, pos:size()[1])
  xc = torch.Tensor(1, deps:size()[1])
  xa[1] = words
  xb[1] = pos
  xc[1] = deps
  local out = model_reentr:forward({xa, xb, xc})
  y = argmax(out)
  return y
end
