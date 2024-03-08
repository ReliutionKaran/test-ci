class Category:
    def __init__(self, name, code, no_of_products):
        self.name = name
        self.code = code
        self.NOP = no_of_products

    def Category_info(categories):
        for category in categories:
            print(
                f"Category: {category.name}\nCode: {category.code}\nNo. of Products: {category.NOP}\n"
            )


class Product(Category):
    def __init__(self, name, code, category, price):
        self.name = name
        self.code = code
        self.category = category.name
        self.price = price
        category.NOP += 1

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
            print(f"{product.name} ({product.category}): {product.price:}")

        # Low to High Sorting
        Product.sorted_products_low_to_high(Products)
        print("\nProducts sorted by price (Low to High):")
        for product in Products:
            print(f"{product.name} ({product.category}): {product.price:}")

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
categories = [C1, C2, C3]

P1 = Product("Laptop", "P01", C1, 70.0)
P2 = Product("Smart Phone", "P02", C1, 10.0)
P3 = Product("Coffie Maker", "P03", C2, 5.5)
P4 = Product("Digital Camera", "P04", C1, 50.0)
P5 = Product("Television", "P05", C1, 12.0)
P6 = Product("Running Shoes", "P06", C3, 1.2)
P7 = Product("Season Bat", "P07", C3, 4.0)
P8 = Product("Kitchen Stove", "P08", C2, 1.5)
P9 = Product("Toaster", "P09", C2, 1.6)
P10 = Product("Cricket Kit", "P10", C3, 17.0)
Products = [P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]

C = Category.Category_info(categories)
print(C)
Product.Product_info(Products)
