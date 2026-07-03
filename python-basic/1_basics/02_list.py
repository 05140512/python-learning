numbers = [1, 2, 3, 4, 5]
names = ['John', 'Jane', 'Jim', 'Jill']
mixed = [1, 'John', True, 2.5]

print('numbers =>', numbers)
print('names =>', names)
print('mixed =>', mixed)

print('numbers[0] =>', numbers[0])
print('names[1] =>', names[1])
print('mixed[2] =>', mixed[2])

print(type(numbers))

fruites = ['apple', 'banana', 'cherry']
# fruites.append('orange') # 尾部追加一个元素
# fruites.insert(1, 'pear') # 在索引1的位置插入一个元素
# fruites.remove('cherry') # 删除一个元素
# fruites.remove('banana') # 删除一个元素
# fruites.remove(fruites[0]) # 删除列表中的第一个元素
# fruites.pop(1)
# fruites.pop(0)
fruites[1] = 'grape' # 修改列表中的元素
print('fruites =>', fruites)

for item in fruites:
  print('item =>', item)

for index, item in enumerate(fruites):
  print('index =>', index, 'item =>', item)

  print('type of fruites =>', type(fruites))
