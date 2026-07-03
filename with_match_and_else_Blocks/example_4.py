from mirror import LookingGlass
manager = LookingGlass()
print("Manager Object : ", manager)

person = manager.__enter__()
if person == 'Aubdur Rob Anik':
    print("right person")

print("Person Name : ", person)

print("Manager Object : ", manager)

manager.__exit__(None, None, None)
print("Person Name : ", person)
