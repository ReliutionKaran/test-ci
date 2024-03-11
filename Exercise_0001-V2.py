class Category:
    def __init__(self, name, code, no_of_products, parent=None, display_name=None):
        self.name = name
        self.code = code
        self.NOP = no_of_products
        self.parent = parent
        self.display_name = display_name
        self.Products = []

    def generate_display_name(self):
        if self.parent
            self.display_name = f"{self.parent.generate_display_name()} > {self.name}"
        else:
            self.display_name = self.name
        return selfdisplay_name

    def add_product(self, product):
        self.Products.append(product)

    def sorting_categories(categories):
        n = len(categories)
        for i in range(n):
            for j in range(0, n - i - 1):
                if categories[j].name > categories[j + 1].name:
                    categories[j], categories[j + 1] = categories[j + 1], categories[j]

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


class Product(Category):
    def __init__(self, name, code, category, price):
        category.add_product(self)
        category.NOP += 1
        self.name = name
        self.code = code
        self.category = category.name
        self.price = price

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


C1 = Category("Electronics", "1", 0)
C2 = Category("Appliances", "2", 0)
C3 = Category("Sports", "3", 0)

Vehicle = Category("Vehicle", "4", 0)
Car = Category("Car", "5", 0, Vehicle)
Petrol = Category("Petrol", "6", 0, Car)
Electric = Category("Electric", "7", 0, Car)
Gas = Category("Gas", "8", 0, Car)

categories = [C1, C2, C3, Vehicle, Car, Petrol, Electric, Gas]

P1 = Product("Laptop", "P001", C1, 50)
P2 = Product("Smart Phone", "P002", C1, 10)
P3 = Product("Coffie Maker", "P003", C2, 5.5)
P4 = Product("Digital Camera", "P004", C1, 50)
P5 = Product("Television", "P005", C1, 12)
P6 = Product("Running Shoes", "P006", C3, 1.2)
P7 = Product("Season Bat", "P007", C3, 4)
P8 = Product("Kitchen Stove", "P008", C2, 1.5)
P9 = Product("Toaster", "P009", C2, 1.6)
P10 = Product("Cricket Kit", "P010", C3, 17)

P11 = Product("TATA Harier", "P011", Car, 150)
P12 = Product("TATA Safari", "P012", Car, 250)
P13 = Product("TATA Altroz", "P013", Car, 100)

P14 = Product("Platina", "P014", Vehicle, 75)
P15 = Product("Pulser", "P015", Vehicle, 90)
P16 = Product("Honda Shine", "P016", Vehicle, 80)

P17 = Product("Toyota Supra", "P017", Petrol, 990)
P18 = Product("Fortuner", "P018", Petrol, 500)
P19 = Product("Thar", "P019", Petrol, 250)

P20 = Product("Nexon EV", "P020", Electric, 900)
P21 = Product("Hundai EV", "P021", Electric, 120)
P22 = Product("Maruti EV", "P022", Electric, 100)

P23 = Product("Swift", "P023", Gas, 700)
P24 = Product("Alto", "P024", Gas, 450)
P25 = Product("Ecco", "P025", Gas, 400)

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
]

C = Category.Category_info(categories)
print(C)
P = Product.Product_info(Products)
P
D = Category.generate_display_name(Petrol)
print(D)
