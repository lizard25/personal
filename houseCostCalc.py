# House cost calculator -- evan
# Plan : / bluepringt
# has a GUI user friendly interface that allows users to input info 
# like cost, HOA fees, property taxes, loan duration, additional principal payments, and interest rate to calculate the total cost of a house over
# the loan duration reutrns the total cost of the house, total interest paid, minimum monthly payment, and the total number of payments made
# at various down payment percentages adjustable with a slider and various loan durations also has capability to input fields just for the user
# not used in calcuations like address a link to the house listing and a field for notes about the house all inputted data is auto saved to a 
# local file, and when the program is launched it will load the data from the file and populate the fields with the saved data
# all houses will be listed tabulary with all exiting fields as different columns and each house as a different row

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser

class HouseCostApp:
    def __init__(self, root):
        self.root = root
        self.root.title("House Cost Calculator")
        self.root.geometry("1100x850")

        self.data_file = "houses_data.json"
        self.houses = self.load_data()

        self.setup_ui()
        self.update_calculations()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.houses, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def setup_ui(self):
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="House Details", padding="15")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Address
        ttk.Label(input_frame, text="Address:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(input_frame, textvariable=self.address_var, width=40)
        self.address_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)

        # Home Price
        ttk.Label(input_frame, text="Home Price ($):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.DoubleVar(value=300000)
        ttk.Entry(input_frame, textvariable=self.price_var).grid(row=1, column=1, sticky=tk.W, pady=5)

        # HOA Fees (Monthly)
        ttk.Label(input_frame, text="HOA (Monthly $):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.hoa_var = tk.DoubleVar(value=0)
        ttk.Entry(input_frame, textvariable=self.hoa_var).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Property Taxes (Yearly)
        ttk.Label(input_frame, text="Property Tax (Yearly %):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tax_rate_var = tk.DoubleVar(value=1.2)
        ttk.Entry(input_frame, textvariable=self.tax_rate_var).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Interest Rate
        ttk.Label(input_frame, text="Interest Rate (%):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.interest_rate_var = tk.DoubleVar(value=6.5)
        ttk.Entry(input_frame, textvariable=self.interest_rate_var).grid(row=4, column=1, sticky=tk.W, pady=5)

        # Loan Duration
        ttk.Label(input_frame, text="Loan Duration (Years):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.IntVar(value=30)
        self.duration_combo = ttk.Combobox(input_frame, textvariable=self.duration_var, values=["10", "15", "20", "30"], width=17)
        self.duration_combo.grid(row=5, column=1, sticky=tk.W, pady=5)

        # Additional Principal
        ttk.Label(input_frame, text="Extra Principal (Monthly $):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.extra_principal_var = tk.DoubleVar(value=0)
        ttk.Entry(input_frame, textvariable=self.extra_principal_var).grid(row=6, column=1, sticky=tk.W, pady=5)

        # Listing Link
        ttk.Label(input_frame, text="Listing Link:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.link_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.link_var, width=40).grid(row=7, column=1, columnspan=2, sticky=tk.W, pady=5)

        # Notes
        ttk.Label(input_frame, text="Notes:").grid(row=8, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(input_frame, width=35, height=5)
        self.notes_text.grid(row=8, column=1, columnspan=2, sticky=tk.W, pady=5)

        # --- Interactive Section ---
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)

        slider_frame = ttk.LabelFrame(right_frame, text="Down Payment", padding="15")
        slider_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.down_payment_pct_var = tk.IntVar(value=20)
        self.down_payment_amt_var = tk.DoubleVar(value=60000)
        
        ttk.Label(slider_frame, text="Down Payment %:").grid(row=0, column=0, sticky=tk.W)
        self.down_payment_slider = ttk.Scale(
            slider_frame, from_=0, to=100, 
            variable=self.down_payment_pct_var, 
            orient=tk.HORIZONTAL, 
            command=self.update_calculations
        )
        self.down_payment_slider.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        pct_entry_frame = ttk.Frame(slider_frame)
        pct_entry_frame.grid(row=2, column=0, pady=5)
        
        ttk.Label(pct_entry_frame, text="Percent:").grid(row=0, column=0, padx=2)
        ttk.Entry(pct_entry_frame, textvariable=self.down_payment_pct_var, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(pct_entry_frame, text="%").grid(row=0, column=2)

        amt_entry_frame = ttk.Frame(slider_frame)
        amt_entry_frame.grid(row=3, column=0, pady=5)
        
        ttk.Label(amt_entry_frame, text="Amount: $").grid(row=0, column=0, padx=2)
        self.down_amt_entry = ttk.Entry(amt_entry_frame, textvariable=self.down_payment_amt_var, width=15)
        self.down_amt_entry.grid(row=0, column=1, padx=5)

        # --- Results Section ---

        results_frame = ttk.LabelFrame(right_frame, text="Financial Summary", padding="15")
        results_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.monthly_payment_var = tk.StringVar(value="$0.00")
        self.total_interest_var = tk.StringVar(value="$0.00")
        self.total_cost_var = tk.StringVar(value="$0.00")
        self.total_payments_var = tk.StringVar(value="0")

        ttk.Label(results_frame, text="Estimated Monthly Payment:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(results_frame, textvariable=self.monthly_payment_var, font=('Helvetica', 14, 'bold'), foreground="blue").grid(row=0, column=1, sticky=tk.E, pady=5)

        ttk.Label(results_frame, text="Total Interest Paid:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(results_frame, textvariable=self.total_interest_var, font=('Helvetica', 11)).grid(row=1, column=1, sticky=tk.E, pady=5)

        ttk.Label(results_frame, text="Total Cost Over Loan:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(results_frame, textvariable=self.total_cost_var, font=('Helvetica', 11, 'bold')).grid(row=2, column=1, sticky=tk.E, pady=5)

        ttk.Label(results_frame, text="Months to Pay Off:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(results_frame, textvariable=self.total_payments_var, font=('Helvetica', 11)).grid(row=3, column=1, sticky=tk.E, pady=5)

        # Buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, pady=20)
        
        ttk.Button(button_frame, text="Save Current House", command=self.add_house).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).grid(row=0, column=1, padx=10)

        # --- Table Section ---
        table_frame = ttk.LabelFrame(main_frame, text="House Comparisons", padding="15")
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("Address", "Price", "HOA", "Int Rate", "Down %", "Monthly", "Total Cost", "Link")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100
            if col == "Address": width = 180
            if col == "Link": width = 150
            self.tree.column(col, width=width, anchor=tk.CENTER)

        self.tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete House", command=self.delete_house)
        self.context_menu.add_command(label="Load into Calculator", command=self.load_house)
        self.context_menu.add_command(label="Open Link", command=self.open_link)

        self.refresh_table()

        self.price_var.trace_add("write", self.on_price_change)
        self.down_payment_pct_var.trace_add("write", self.on_pct_change)
        self.down_payment_amt_var.trace_add("write", self.on_amt_change)
        
        for var in [self.hoa_var, self.tax_rate_var, self.interest_rate_var, self.duration_var, self.extra_principal_var]:
            var.trace_add("write", lambda *args: self.update_calculations())

    def on_price_change(self, *args):
        if not hasattr(self, '_updating_flag'):
            self._updating_flag = True
            try:
                price = self.price_var.get()
                pct = self.down_payment_pct_var.get()
                self.down_payment_amt_var.set(round(price * (pct / 100.0), 2))
            except: pass
            self._updating_flag = False
        self.update_calculations()

    def on_pct_change(self, *args):
        if not hasattr(self, '_updating_flag') or not self._updating_flag:
            self._updating_flag = True
            try:
                price = self.price_var.get()
                pct = self.down_payment_pct_var.get()
                self.down_payment_amt_var.set(round(price * (pct / 100.0), 2))
            except: pass
            self._updating_flag = False
        self.update_calculations()

    def on_amt_change(self, *args):
        if not hasattr(self, '_updating_flag') or not self._updating_flag:
            self._updating_flag = True
            try:
                price = self.price_var.get()
                amt = self.down_payment_amt_var.get()
                if price > 0:
                    self.down_payment_pct_var.set(int((amt / price) * 100))
            except: pass
            self._updating_flag = False
        self.update_calculations()

    def update_calculations(self, *args):
        try:
            price = float(self.price_var.get())
            down_amt = float(self.down_payment_amt_var.get())
            hoa = float(self.hoa_var.get())
            tax_rate = float(self.tax_rate_var.get()) / 100
            annual_interest = float(self.interest_rate_var.get()) / 100
            years = int(self.duration_var.get())
            extra_principal = float(self.extra_principal_var.get())

            loan_amount = price - down_amt
            monthly_interest = annual_interest / 12
            total_months = years * 12

            # Basic Monthly P&I
            if monthly_interest > 0:
                monthly_pi = loan_amount * (monthly_interest * (1 + monthly_interest) ** total_months) / ((1 + monthly_interest) ** total_months - 1)
            else:
                monthly_pi = loan_amount / total_months if total_months > 0 else 0

            monthly_tax = (price * tax_rate) / 12
            # Monthly PITI + HOA (Principal, Interest, Tax, Insurance - Insurance omitted unless specified, HOA added)
            total_monthly_payment = monthly_pi + hoa + monthly_tax

            # Amortization simulation for extra principal
            balance = loan_amount
            total_interest_paid = 0.0
            months_count = 0
            
            if loan_amount > 0:
                while balance > 0.01 and months_count < 600: # 50 year limit safety
                    interest_charge = balance * monthly_interest
                    # Standard payment part towards principal
                    principal_part = monthly_pi - interest_charge
                    
                    # Total principal reduction including extra
                    reduction = principal_part + extra_principal
                    
                    if reduction > balance:
                        reduction = balance
                    
                    balance -= reduction
                    total_interest_paid += interest_charge
                    months_count += 1
            else:
                months_count = 0
                total_interest_paid = 0.0

            # Total cost calculation
            total_cost = float(price) + float(total_interest_paid) + (float(hoa) + float(monthly_tax)) * int(months_count)

            self.monthly_payment_var.set(f"${total_monthly_payment:,.2f}")
            self.total_interest_var.set(f"${total_interest_paid:,.2f}")
            self.total_cost_var.set(f"${total_cost:,.2f}")
            self.total_payments_var.set(f"{months_count}")
            
        except Exception:
            pass

    def add_house(self):
        address = self.address_var.get().strip()
        if not address:
            messagebox.showwarning("Input Required", "Please enter an address.")
            return

        try:
            house = {
                "Address": address,
                "Price": f"${self.price_var.get():,.0f}",
                "HOA": f"${self.hoa_var.get():,.0f}",
                "Interest Rate": f"{self.interest_rate_var.get()}%",
                "Down %": f"{self.down_payment_pct_var.get()}%",
                "Monthly": self.monthly_payment_var.get(),
                "Total Cost": self.total_cost_var.get(),
                "Link": self.link_var.get(),
                "Raw Data": {
                    "address": address,
                    "price": self.price_var.get(),
                    "hoa": self.hoa_var.get(),
                    "tax_rate": self.tax_rate_var.get(),
                    "interest_rate": self.interest_rate_var.get(),
                    "duration": self.duration_var.get(),
                    "extra_principal": self.extra_principal_var.get(),
                    "down_payment_pct": self.down_payment_pct_var.get(),
                    "down_payment_amt": self.down_payment_amt_var.get(),
                    "link": self.link_var.get(),
                    "notes": self.notes_text.get("1.0", tk.END).strip()
                }
            }
            # Update existing or add new
            existing_idx = next((i for i, h in enumerate(self.houses) if h["Address"] == address), -1)
            if existing_idx >= 0:
                self.houses[existing_idx] = house
            else:
                self.houses.append(house)
            
            self.save_data()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save house: {e}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for h in self.houses:
            self.tree.insert("", tk.END, values=(
                h["Address"], h["Price"], h["HOA"], h["Interest Rate"], 
                h["Down %"], h["Monthly"], h["Total Cost"], h.get("Link", "")
            ))

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if item and column == "#8": # Link column
            self.open_link()

    def open_link(self):
        selection = self.tree.selection()
        if not selection: return
        
        item = selection[0]
        values = self.tree.item(item)['values']
        if len(values) > 7:
            link = values[7]
            if link and str(link).startswith("http"):
                webbrowser.open(str(link))
            elif link:
                messagebox.showinfo("Link", f"Invalid URL: {link}")

    def delete_house(self):

        selection = self.tree.selection()
        if not selection: return
        
        item = selection[0]
        values = self.tree.item(item)['values']
        address = values[0]
        
        self.houses = [h for h in self.houses if h["Address"] != address]
        self.save_data()
        self.refresh_table()

    def load_house(self):
        selection = self.tree.selection()
        if not selection: return
        
        item = selection[0]
        address = self.tree.item(item)['values'][0]
        house = next((h for h in self.houses if h["Address"] == address), None)
        
        if house and "Raw Data" in house:
            raw = house["Raw Data"]
            self.address_var.set(raw.get("address", ""))
            self.price_var.set(raw.get("price", 300000))
            self.hoa_var.set(raw.get("hoa", 0))
            self.tax_rate_var.set(raw.get("tax_rate", 1.2))
            self.interest_rate_var.set(raw.get("interest_rate", 6.5))
            self.duration_var.set(raw.get("duration", 30))
            self.extra_principal_var.set(raw.get("extra_principal", 0))
            self.down_payment_pct_var.set(raw.get("down_payment_pct", 20))
            self.down_payment_amt_var.set(raw.get("down_payment_amt", 60000))
            self.link_var.set(raw.get("link", ""))
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", raw.get("notes", ""))
            self.update_calculations()


    def clear_fields(self):
        self.address_var.set("")
        self.price_var.set(300000)
        self.hoa_var.set(0)
        self.tax_rate_var.set(1.2)
        self.interest_rate_var.set(6.5)
        self.duration_var.set(30)
        self.extra_principal_var.set(0)
        self.down_payment_pct_var.set(20)
        self.down_payment_amt_var.set(60000)
        self.link_var.set("")
        self.notes_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = HouseCostApp(root)
    root.mainloop()

