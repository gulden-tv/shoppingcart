#!/usr/bin/python3

import sys
import dbm

products = [
    {
        "id": "e182115a-63d2-42ce-8fe0-5f696ecdfba6",
        "name": "Brilliant Watch",
        "price": "250.00",
        "stock": 2
    },
    {
        "id": "f9a6d214-1c38-47ab-a61c-c99a59438b12",
        "name": "Old fashion cellphone",
        "price": "24.00",
        "stock": 2
    },
    {
        "id": "1f1321bb-0542-45d0-9601-2a3d007d5842",
        "name": "Modern iPhone",
        "price": "1000.00",
        "stock": 2
    },
    {
        "id": "f5384efc-eadb-4d7b-a131-36516269c218",
        "name": "Beautiful Sunglasses",
        "price": "12.00",
        "stock": 2
    },
    {
        "id": "6d6ca89d-fbc2-4fc2-93d0-6ee46ae97345",
        "name": "Stylish Cup",
        "price": "8.00",
        "stock": 2
    },
    {
        "id": "efe0c7a3-9835-4dfb-87e1-575b7d06701a",
        "name": "Herb caps",
        "price": "12.00",
        "stock": 2
    },
    {
        "id": "x341115a-63d2-42ce-8fe0-5f696ecdfca6",
        "name": "Audiophile Headphones",
        "price": "550.00",
        "stock": 2
    },
    {
        "id": "42860491-9f15-43d4-adeb-0db2cc99174a",
        "name": "Digital Camera",
        "price": "225.00",
        "stock": 2
    },
    {
        "id": "63a3c635-4505-4588-8457-ed04fbb76511",
        "name": "Empty Bluray Disc",
        "price": "5.00",
        "stock": 2
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96239",
        "name": "256GB Pendrive",
        "price": "60.00",
        "stock": 2
    },
    {
        "id": "97a19842-db31-4537-9241-505111c96239",
        "name": "Mac book air",
        "price": "1500.00",
        "stock": 5
    },
    {
        "id": "97a19842-db31-4537-9999-505322296239",
        "name": "iPhone 15 pro Max",
        "price": "999.00",
        "stock": 7
    },
    {
        "id": "97a19844-d431-4557-9241-505333396239",
        "name": "Xiaomi phone",
        "price": "899.00",
        "stock": 5
    },
    {
        "id": "97a19842-db31-4537-9666-505344496239",
        "name": "Sun glasses",
        "price": "100.00",
        "stock": 9
    },
    {
        "id": "97a12345-db31-4537-9241-505355596239",
        "name": "512GB Pendrive",
        "price": "90.00",
        "stock": 3
    },
    {
        "id": "97a19842-db31-4537-9241-50666796231",
        "name": "Pen",
        "price": "2.00",
        "stock": 20
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96232",
        "name": "Pencil",
        "price": "1.00",
        "stock": 200
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96233",
        "name": "Paper A4",
        "price": "10.00",
        "stock": 50
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96234",
        "name": "Paper A3",
        "price": "15.00",
        "stock": 200
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96235",
        "name": "Super eraser",
        "price": "6.00",
        "stock": 70
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96236",
        "name": "Nuts",
        "price": "7.00",
        "stock": 25
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96237",
        "name": "Cake",
        "price": "10.00",
        "stock": 29
    },
    {
        "id": "97a19842-db31-4537-9241-5053d7c96238",
        "name": "Bread",
        "price": "6.00",
        "stock": 49
    }
]


csv = open("products.csv", "w")
csv.write("id;name;price;stock\n")

for p in products:
    # print(int(k), db[k].decode())
    # csv.write(str(int(k)) + ";" + db[k].decode() + "\n")
    csv.write(p['id'] + ";" + p['name'] + ";" + p['price'] + ";" + str(p['stock']) + "\n")
    print(p['id'])

csv.close()

