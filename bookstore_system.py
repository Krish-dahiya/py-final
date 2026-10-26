import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Bookstore:
    def __init__(self):
        self.inventory = pd.read_csv("inventory.csv")
        self.sales = pd.read_csv("sales.csv")

    def save_data(self):
        self.inventory.to_csv("inventory.csv", index=False)
        self.sales.to_csv("sales.csv", index=False)

    def add_book(self, title, author, genre, price, quantity):
        if not title.strip() or price <= 0 or quantity < 0:
            print("Invalid details!")
            return
        if title.lower() in self.inventory["Title"].str.lower().values:
            print("Book already exists!")
            return
        self.inventory.loc[len(self.inventory)] = [title, author, genre, price, quantity]
        self.save_data()
        print("Book added.")

    def remove_book(self, title):
        found = self.inventory["Title"].str.lower() == title.lower()
        if found.any():
            self.inventory = self.inventory[~found].reset_index(drop=True)
            self.save_data()
            print("Book removed.")
        else:
            print("Book not found.")

    def update_inventory(self, title, quantity):
        found = self.inventory["Title"].str.lower() == title.lower()
        if not found.any():
            print("Book not found.")
        elif quantity < 0:
            print("Quantity cannot be negative.")
        else:
            self.inventory.loc[found, "Quantity"] = quantity
            self.save_data()
            print("Stock updated.")

    def record_sale(self, title, quantity):
        found = self.inventory["Title"].str.lower() == title.lower()
        if not found.any():
            print("Book not found.")
            return
        if quantity <= 0:
            print("Quantity must be positive.")
            return
        i = self.inventory.index[found][0]
        if quantity > self.inventory.loc[i, "Quantity"]:
            print("Not enough stock.")
            return
        revenue = self.inventory.loc[i, "Price"] * quantity
        self.inventory.loc[i, "Quantity"] -= quantity
        self.sales.loc[len(self.sales)] = [
            pd.Timestamp.today().strftime("%Y-%m-%d"),
            self.inventory.loc[i, "Title"], quantity, revenue
        ]
        self.save_data()
        print("Sale saved. Revenue = Rs.", revenue)

    def generate_report(self):
        print("\nINVENTORY")
        print(self.inventory.to_string(index=False))
        print("\nSALES REPORT")
        if self.sales.empty:
            print("No sales yet.")
            return
        print("Total books sold:", int(np.sum(self.sales["Quantity Sold"])))
        print("Total revenue: Rs.", round(np.sum(self.sales["Total Revenue"]), 2))
        print("Average sale revenue:", round(np.mean(self.sales["Total Revenue"]), 2))
        print("\nBest-selling books:")
        print(self.sales.groupby("Title")["Quantity Sold"].sum().sort_values(ascending=False))

    def show_charts(self):
        if self.sales.empty:
            print("No sales data.")
            return
        sns.set_theme(style="whitegrid")

        self.sales.groupby("Title")["Quantity Sold"].sum().plot(kind="bar")
        plt.title("Books Sold")
        plt.xlabel("Book")
        plt.ylabel("Quantity Sold")
        plt.tight_layout()
        plt.show()

        data = self.sales.copy()
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data = data.dropna(subset=["Date"])
        data["Month"] = data["Date"].dt.to_period("M").astype(str)
        data.groupby("Month")["Total Revenue"].sum().plot(marker="o")
        plt.title("Monthly Revenue")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.tight_layout()
        plt.show()

        genre_data = self.sales.merge(self.inventory[["Title", "Genre"]], on="Title", how="left")
        genre_data.groupby("Genre")["Total Revenue"].sum().plot(kind="pie", autopct="%1.1f%%")
        plt.title("Revenue by Genre")
        plt.ylabel("")
        plt.tight_layout()
        plt.show()

        sns.heatmap(self.sales[["Quantity Sold", "Total Revenue"]].corr(), annot=True, cmap="coolwarm")
        plt.title("Sales Heatmap")
        plt.tight_layout()
        plt.show()

def main():
    shop = Bookstore()
    while True:
        print("\nBOOKSTORE SYSTEM")
        print("1. Show inventory")
        print("2. Add book")
        print("3. Remove book")
        print("4. Update stock")
        print("5. Record sale")
        print("6. Sales report")
        print("7. Show graphs")
        print("8. Exit")
        choice = input("Choose 1-8: ")
        try:
            if choice == "1":
                print(shop.inventory.to_string(index=False))
            elif choice == "2":
                title = input("Title: ")
                author = input("Author: ")
                genre = input("Genre: ")
                price = float(input("Price: "))
                quantity = int(input("Quantity: "))
                shop.add_book(title, author, genre, price, quantity)
            elif choice == "3":
                shop.remove_book(input("Title to remove: "))
            elif choice == "4":
                title = input("Title: ")
                quantity = int(input("New quantity: "))
                shop.update_inventory(title, quantity)
            elif choice == "5":
                title = input("Title: ")
                quantity = int(input("Quantity sold: "))
                shop.record_sale(title, quantity)
            elif choice == "6":
                shop.generate_report()
            elif choice == "7":
                shop.show_charts()
            elif choice == "8":
                shop.save_data()
                print("Goodbye!")
                break
            else:
                print("Choose a number from 1 to 8.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
