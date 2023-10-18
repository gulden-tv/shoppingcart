import os
os.system("redis-export 'order-' ~/orders.json -a please")
os.system("redis-export 'products*' ~/products.json -a please")


