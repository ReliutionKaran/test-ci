# Category Class
class Category:
    def __init__(self, name, code, no_of_products, parent=None, display_name=None)
        self.name = name
        self.code = code
        self.NOP = no_of_products
        self.parent = parent
        self.display_name = display_name
        self.Products = []

    # Generate Display Name.(Used Recursion Method)
    def generate_display_name(self):
        if self.parent:
            self.display_name = f"{self.parent.generate_display_name()} > {self.name}"
        else:
            self.display_name = self.name
        return self.display_name

    # This function append a product for its specific Category, from List of products.
    def add_product(self, product):
        self.Products.append(product)

    # Sorting Categories from Bubble Sorting Method by name (Alphabetical Manner)
    def sorting_categories(categories):
        n = len(categories)
        for i in range(n):
            for j in range(0, n - i - 1):
                if categories[j].name > categories[j + 1].name:
                    categories[j], categories[j + 1] = categories[j + 1], categories[j]

    # Print All Info of category class
    def Category_info(categories):
        Category.sorting_categories(categories)
        for category in categories:
            print(
                f"Category: {category.name}\nCode: {category.code}\nNo. of Products: {category.NOP}\n"
            )
            for product in category.Products:
                print(
                    f"Product: {product.name} (Code: {product.code}, Price: {product.price:.3f})"
                )
            print("\n")


# Product Class
class Product(Category):
    def __init__(self, name, code, category, price):
        category.add_product(self)
        category.NOP += 1
        self.name = name
        self.code = code
        self.category = category.name
        self.price = price
        self.stock_at_locations = {}

    # If the location is already known, it updates the stock quantity, otherwise
    # it adds a new entry for that location in the stock dictionary.
    def add_stock_at_location(self, location, quantity):
        self.stock_at_locations[location] = quantity

    # It will update stock of products at desiered location.
    def update_stock_of_products(Products, location, stock_quantity):
        for product in Products:
            product.add_stock_at_location(location, stock_quantity)
            print(
                f"{product.name} Stock at {L1.name}: {product.stock_at_locations.get(L1, 0)}"
            )

    # It will display product detail with it's stock.
    @staticmethod
    def display_product_with_stock(Products):
        print("\n Display product with it's stock...")
        for product in Products:
            print(f"\nProduct Details for {product.name} ({product.category}):")
            print(f"Code: {product.code}")
            print(f"Price: {product.price:.3f}")

            stock_at_location = product.stock_at_locations
            if stock_at_location:
                print("Stock at Various Locations:")
                for location, stock in stock_at_location.items():
                    print(f"{location}: {stock} units")
            else:
                print("No stock information available for this product.")

    # This function will display various products at various locations.
    @staticmethod
    def display_products_location(Products, locations):
        for location in locations:
            print(f"\nProducts at {location.name}:")
            location_products = [
                product
                for product in Products
                if location in product.stock_at_locations
            ]

            if location_products:
                for product in location_products:
                    print(f"{product.name} ({product.category}): {product.price:.3f}")
            else:
                print("No products available.")

    # Sort and print products based on price (High to Low)
    @staticmethod
    def sorted_products_high_to_low(Products):
        for i in range(0, len(Products)):
            for j in range(i + 1, len(Products)):
                if Products[i].price <= Products[j].price:
                    Products[i], Products[j] = Products[j], Products[i]

    # Sort and print products based on price (Low to High)
    @staticmethod
    def sorted_products_low_to_high(Products):
        for i in range(0, len(Products)):
            for j in range(i + 1, len(Products)):
                if Products[i].price >= Products[j].price:
                    Products[i], Products[j] = Products[j], Products[i]

    # Search Products from code
    @staticmethod
    def find_products(Products, target_code):
        find_products = next(
            (product for product in Products if product.code == target_code)
        )
        return find_products

    def Product_info(Products):
        # High to low Sorting
        print("Products sorted by price (High to Low):")
        Product.sorted_products_high_to_low(Products)
        for product in Products:
            print(f"{product.name} ({product.category}): {product.price:.3f}")

        # Low to High Sorting
        Product.sorted_products_low_to_high(Products)
        print("\nProducts sorted by price (Low to High):")
        for product in Products:
            print(f"{product.name} ({product.category}): {product.price:.3f}")

        # Searching of Product
        target_code = input("Enter the code: ")
        found_products = Product.find_products(Products, target_code)

        if found_products:
            print(
                f"Product found: {found_products.name} (Code: {found_products.code}, Category: {found_products.category}, Price: {found_products.price:.3f})"
            )
        else:
            print(f"Product with code '{target_code}' not found.")


# Class Location
class Location:
    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __str__(self):
        return f"{self.name} ({self.code})"


# Class Location
class Movement:
    def __init__(self, from_location, to_location, product, quantity):
        self.FL = from_location
        self.TL = to_location
        self.product = product
        self.quantity = quantity

    # This function will move products from one location to noteher location.
    def move_product(movements):
        for movement in movements:
            from_location = movement.FL
            to_location = movement.TL
            product = movement.product
            quantity = movement.quantity

            # Check if product at from_location.
            if (
                from_location in product.stock_at_locations
                and product.stock_at_locations[from_location] >= quantity
            ):
                # Move the quantity from FL to TL.
                product.stock_at_locations[from_location] -= quantity
                if to_location in product.stock_at_locations:
                    product.stock_at_locations[to_location] += quantity
                else:
                    product.stock_at_locations[to_location] = quantity
                print(
                    f"Moved {quantity} units of {product.name} from {from_location} to {to_location}."
                )
            else:
                print(
                    f"Error: Insufficient stock of {product.name} at {from_location}."
                )


C1 = Category("Electronics", "1", 0)
C2 = Category("Appliances", "2", 0)
C3 = Category("Sports", "3", 0)
Vehicle = Category("Vehicle", "4", 0)
Car = Category("Car", "5", 0, Vehicle)
Petrol = Category("Petrol", "6", 0, Car)
Electric = Category("Electric", "7", 0, Car)
Gas = Category("Gas", "8", 0, Car)
categories = [C1, C2, C3, Vehicle, Car, Petrol, Electric, Gas]

P1 = Product("Laptop", "P001", C1, 50.000)
P2 = Product("Smart Phone", "P002", C1, 10.000)
P3 = Product("Coffie Maker", "P003", C2, 5.500)
P4 = Product("Digital Camera", "P004", C1, 50.000)
P5 = Product("Television", "P005", C1, 12.000)
P6 = Product("Running Shoes", "P006", C3, 1.200)
P7 = Product("Season Bat", "P007", C3, 4.000)
P8 = Product("Kitchen Stove", "P008", C2, 1.500)
P9 = Product("Toaster", "P009", C2, 1.600)
P10 = Product("Cricket Kit", "P010", C3, 17.000)
P11 = Product("TATA Harier", "P011", Car, 150.000)
P12 = Product("TATA Safari", "P012", Car, 250.000)
P13 = Product("TATA Altroz", "P013", Car, 100.000)
P14 = Product("Platina", "P014", Vehicle, 75.000)
P15 = Product("Pulser", "P015", Vehicle, 90.000)
P16 = Product("Honda Shine", "P016", Vehicle, 80.000)
P17 = Product("Toyota Supra", "P017", Petrol, 990.000)
P18 = Product("Fortuner", "P018", Petrol, 500.000)
P19 = Product("Thar", "P019", Petrol, 250.000)
P20 = Product("Nexon EV", "P020", Electric, 900.000)
P21 = Product("Hundai EV", "P021", Electric, 120.000)
P22 = Product("Maruti EV", "P022", Electric, 100.000)
P23 = Product("Swift", "P023", Gas, 700.000)
P24 = Product("Alto", "P024", Gas, 450.000)
P25 = Product("Ecco", "P025", Gas, 400.000)
P26 = Product("Knife", "P026", C2, 1.000)
P27 = Product("Spoon", "P027", C2, 1.200)
P28 = Product("Tennis Balls", "P028", C3, 6.000)
P29 = Product("Season Balls", "P029", C3, 12.000)
P30 = Product("Air Cooler", "P030", C1, 15.000)
Products = [
    P1,
    P2,
    P3,
    P4,
    P5,
    P6,
    P7,
    P8,
    P9,
    P10,
    P11,
    P12,
    P13,
    P14,
    P15,
    P16,
    P17,
    P18,
    P19,
    P20,
    P21,
    P22,
    P23,
    P24,
    P25,
    P26,
    P27,
    P28,
    P29,
    P30,
]

L1 = Location("Stock Hall A", "A0001")
L2 = Location("Stock Hall B", "B0002")
L3 = Location("Stock Hall C", "C0003")
L4 = Location("Stock Hall D", "D0004")
locations = [L1, L2, L3, L4]

movement1 = Movement(L1, L2, P26, 10)
movement2 = Movement(L1, L3, P27, 5)
movement3 = Movement(L1, L4, P30, 3)
movement4 = Movement(L1, L4, P28, 12)
movement5 = Movement(L1, L4, P29, 17)
movements = [movement1, movement2, movement3, movement4, movement5]

a = Category.Category_info(categories)
print(a)
b = Product.Product_info(Products)
print(b)
c = Category.generate_display_name(Petrol)
print(c)

A = Product.update_stock_of_products(Products, L1, 20)
print(A)
B = Movement.move_product(movements)
print(B)
C = Product.display_product_with_stock(Products)
print(C)
D = Product.display_products_location(Products, locations)
print(D)
