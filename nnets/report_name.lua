--require 'cunn'
require 'dp'
require 'optim'
require 'nngraph'

model = arg[1]

xp = torch.load(model)
train_loss = xp:optimizer():report()["loss"]
train_acc = xp:optimizer():report()["feedback"]["confusion"]["accuracy"]
valid_acc = xp:validator():report()["feedback"]["confusion"]["accuracy"]
print("Training loss: " .. train_loss)
print("Training accuracy: " .. train_acc)
print("Validation accuracy: " .. valid_acc)
perclass = xp:validator():report()["feedback"]["confusion"]["per_class"]["accuracy"]
print(perclass)
print("")

