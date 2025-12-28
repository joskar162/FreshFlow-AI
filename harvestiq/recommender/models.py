from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Customer {self.customer_id}"

class Product(models.Model):
    product_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    surplus_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"Product {self.product_id}: {self.name}"

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction: {self.customer} - {self.product} - {self.quantity} on {self.purchase_date}"