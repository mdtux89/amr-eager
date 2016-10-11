--require 'cunn'
require 'dp'
require 'optim'
require 'nngraph'

model_dir = arg[1]

print("rels classifier")
xp = torch.load(model_dir .. "/model_rels.dat")
train_loss = xp:optimizer():report()["loss"]
train_acc = xp:optimizer():report()["feedback"]["confusion"]["accuracy"]
valid_acc = xp:validator():report()["feedback"]["confusion"]["accuracy"]
print("Training loss: " .. train_loss)
print("Training accuracy: " .. train_acc)
print("Validation accuracy: " .. valid_acc)
print("Confusion matrix:")
print(xp:validator():report()["feedback"]["confusion"]["matrix"])
perclass = xp:validator():report()["feedback"]["confusion"]["per_class"]["accuracy"]
print("Accuracy SHIFT: " .. perclass[1])
print("Accuracy REDUCE: " .. perclass[2])
print("Accuracy LARC1: " .. perclass[3])
print("Accuracy RARC1: " .. perclass[4])
print("")

print("labels classifier")
xp = torch.load(model_dir .. "/model_labels.dat")
train_loss = xp:optimizer():report()["loss"]
train_acc = xp:optimizer():report()["feedback"]["confusion"]["accuracy"]
valid_acc = xp:validator():report()["feedback"]["confusion"]["accuracy"]
print("Training loss: " .. train_loss)
print("Training accuracy: " .. train_acc)
print("Validation accuracy: " .. valid_acc)
print("")

print("reentr classifier")
xp = torch.load(model_dir .. "/model_reentr.dat")
train_loss = xp:optimizer():report()["loss"]
train_acc = xp:optimizer():report()["feedback"]["confusion"]["accuracy"]
valid_acc = xp:validator():report()["feedback"]["confusion"]["accuracy"]
print("Training loss: " .. train_loss)
print("Training accuracy: " .. train_acc)
print("Validation accuracy: " .. valid_acc)
print("Confusion matrix:")
print(xp:validator():report()["feedback"]["confusion"]["matrix"])
perclass = xp:validator():report()["feedback"]["confusion"]["per_class"]["accuracy"]
print("Accuracy REENTR: " .. perclass[1])
print("Accuracy NONREENTR: " .. perclass[2])
print("")

