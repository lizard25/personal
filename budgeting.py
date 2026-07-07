import json
import os
import tkinter as tk
from tkinter import messagebox, ttk


class BudgetingApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Budget Planner")
		self.root.geometry("1250x920")

		self.data_file = "budgeting_data.json"
		self.budgets = self.load_data()

		self.expense_rows = []

		self.setup_ui()
		self.update_calculations()

	def load_data(self):
		if os.path.exists(self.data_file):
			try:
				with open(self.data_file, "r", encoding="utf-8") as file_handle:
					return json.load(file_handle)
			except (OSError, json.JSONDecodeError):
				return []
		return []

	def save_data(self):
		try:
			with open(self.data_file, "w", encoding="utf-8") as file_handle:
				json.dump(self.budgets, file_handle, indent=4)
		except OSError as error:
			messagebox.showerror("Save Error", f"Could not save budget data: {error}")

	def setup_ui(self):
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		container = ttk.Frame(self.root)
		container.grid(row=0, column=0, sticky="nsew")
		container.columnconfigure(0, weight=1)
		container.rowconfigure(0, weight=1)

		self.scroll_canvas = tk.Canvas(container, highlightthickness=0)
		self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

		y_scroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.scroll_canvas.yview)
		y_scroll.grid(row=0, column=1, sticky="ns")
		x_scroll = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.scroll_canvas.xview)
		x_scroll.grid(row=1, column=0, sticky="ew")

		self.scroll_canvas.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

		content_frame = ttk.Frame(self.scroll_canvas)
		self.scroll_window_id = self.scroll_canvas.create_window((0, 0), window=content_frame, anchor="nw")

		def update_scroll_region(_event=None):
			self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

		def resize_inner_window(event):
			self.scroll_canvas.itemconfigure(self.scroll_window_id, width=event.width)

		content_frame.bind("<Configure>", update_scroll_region)
		self.scroll_canvas.bind("<Configure>", resize_inner_window)

		self.root.bind_all(
			"<MouseWheel>",
			lambda event: self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"),
		)
		self.root.bind_all(
			"<Shift-MouseWheel>",
			lambda event: self.scroll_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"),
		)

		notebook = ttk.Notebook(content_frame)
		notebook.grid(row=0, column=0, sticky="nsew")

		tab_planner = ttk.Frame(notebook)
		tab_saved = ttk.Frame(notebook)
		notebook.add(tab_planner, text="Budget Planner")
		notebook.add(tab_saved, text="Saved Budgets")

		planner_frame = ttk.Frame(tab_planner, padding="15")
		planner_frame.grid(row=0, column=0, sticky="nsew")
		planner_frame.columnconfigure(0, weight=1)
		planner_frame.columnconfigure(1, weight=1)

		input_frame = ttk.LabelFrame(planner_frame, text="Budget Inputs", padding="15")
		input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
		input_frame.columnconfigure(1, weight=1)

		ttk.Label(input_frame, text="Budget Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
		self.budget_name_var = tk.StringVar()
		ttk.Entry(input_frame, textvariable=self.budget_name_var, width=36).grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)

		ttk.Label(input_frame, text="Income Amount ($):").grid(row=1, column=0, sticky=tk.W, pady=5)
		self.income_amount_var = tk.DoubleVar(value=5000)
		ttk.Entry(input_frame, textvariable=self.income_amount_var).grid(row=1, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Income Frequency:").grid(row=2, column=0, sticky=tk.W, pady=5)
		self.income_frequency_var = tk.StringVar(value="Monthly")
		ttk.Combobox(
			input_frame,
			textvariable=self.income_frequency_var,
			values=["Weekly", "Biweekly", "Monthly", "Annually"],
			state="readonly",
			width=18,
		).grid(row=2, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Savings Amount ($):").grid(row=3, column=0, sticky=tk.W, pady=5)
		self.savings_amount_var = tk.DoubleVar(value=500)
		ttk.Entry(input_frame, textvariable=self.savings_amount_var).grid(row=3, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Savings Frequency:").grid(row=4, column=0, sticky=tk.W, pady=5)
		self.savings_frequency_var = tk.StringVar(value="Monthly")
		ttk.Combobox(
			input_frame,
			textvariable=self.savings_frequency_var,
			values=["Weekly", "Biweekly", "Monthly", "Annually"],
			state="readonly",
			width=18,
		).grid(row=4, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Notes:").grid(row=5, column=0, sticky=tk.NW, pady=5)
		self.notes_text = tk.Text(input_frame, width=35, height=5)
		self.notes_text.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5)

		expenses_frame = ttk.LabelFrame(input_frame, text="Expenses", padding="10")
		expenses_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(10, 5))
		expenses_frame.columnconfigure(0, weight=1)

		header_frame = ttk.Frame(expenses_frame)
		header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
		header_frame.columnconfigure(1, weight=1)

		ttk.Label(header_frame, text="Name", width=24).grid(row=0, column=0, sticky=tk.W)
		ttk.Label(header_frame, text="Amount ($)", width=16).grid(row=0, column=1, sticky=tk.W)
		ttk.Label(header_frame, text="Frequency", width=14).grid(row=0, column=2, sticky=tk.W)

		self.expenses_rows_frame = ttk.Frame(expenses_frame)
		self.expenses_rows_frame.grid(row=1, column=0, sticky="nsew")
		self.expenses_rows_frame.columnconfigure(0, weight=1)

		expense_button_frame = ttk.Frame(expenses_frame)
		expense_button_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))
		ttk.Button(expense_button_frame, text="Add Expense", command=self.add_expense_row).grid(row=0, column=0, padx=(0, 8))
		ttk.Button(expense_button_frame, text="Remove Last", command=self.remove_last_expense_row).grid(row=0, column=1)

		summary_frame = ttk.LabelFrame(planner_frame, text="Budget Summary", padding="15")
		summary_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

		self.monthly_income_var = tk.StringVar(value="$0.00")
		self.yearly_income_var = tk.StringVar(value="$0.00")
		self.monthly_savings_var = tk.StringVar(value="$0.00")
		self.yearly_savings_var = tk.StringVar(value="$0.00")
		self.monthly_expenses_var = tk.StringVar(value="$0.00")
		self.yearly_expenses_var = tk.StringVar(value="$0.00")
		self.monthly_net_var = tk.StringVar(value="$0.00")
		self.yearly_net_var = tk.StringVar(value="$0.00")

		ttk.Label(summary_frame, text="Monthly Income:").grid(row=0, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.monthly_income_var, font=("Helvetica", 12, "bold")).grid(row=0, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Yearly Income:").grid(row=1, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.yearly_income_var).grid(row=1, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Monthly Savings:").grid(row=2, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.monthly_savings_var).grid(row=2, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Yearly Savings:").grid(row=3, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.yearly_savings_var).grid(row=3, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Monthly Expenses:").grid(row=4, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.monthly_expenses_var).grid(row=4, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Yearly Expenses:").grid(row=5, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.yearly_expenses_var).grid(row=5, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Monthly Net:").grid(row=6, column=0, sticky=tk.W, pady=5)
		self.monthly_net_label = ttk.Label(summary_frame, textvariable=self.monthly_net_var, font=("Helvetica", 12, "bold"))
		self.monthly_net_label.grid(row=6, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Yearly Net:").grid(row=7, column=0, sticky=tk.W, pady=5)
		self.yearly_net_label = ttk.Label(summary_frame, textvariable=self.yearly_net_var, font=("Helvetica", 12, "bold"))
		self.yearly_net_label.grid(row=7, column=1, sticky=tk.E, pady=5)

		action_frame = ttk.Frame(summary_frame)
		action_frame.grid(row=8, column=0, columnspan=2, pady=(15, 0))
		ttk.Button(action_frame, text="Save Budget", command=self.add_budget).grid(row=0, column=0, padx=8)
		ttk.Button(action_frame, text="Clear Fields", command=self.clear_fields).grid(row=0, column=1, padx=8)
		ttk.Button(action_frame, text="View Saved Budgets", command=lambda: notebook.select(tab_saved)).grid(row=0, column=2, padx=8)

		saved_frame = ttk.Frame(tab_saved, padding="15")
		saved_frame.grid(row=0, column=0, sticky="nsew")
		saved_frame.columnconfigure(0, weight=1)
		saved_frame.rowconfigure(0, weight=1)

		columns = ("Budget Name", "Income", "Savings", "Monthly Expenses", "Monthly Net", "Yearly Net")
		self.tree = ttk.Treeview(saved_frame, columns=columns, show="headings", height=18)
		for column_name in columns:
			self.tree.heading(column_name, text=column_name)
			width = 170
			if column_name == "Budget Name":
				width = 240
			self.tree.column(column_name, width=width, anchor=tk.CENTER)

		self.tree.grid(row=0, column=0, sticky="nsew")
		table_scroll = ttk.Scrollbar(saved_frame, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscrollcommand=table_scroll.set)
		table_scroll.grid(row=0, column=1, sticky="ns")

		self.tree.bind("<Button-3>", self.show_context_menu)
		self.tree.bind("<Double-1>", self.on_double_click)

		self.context_menu = tk.Menu(self.root, tearoff=0)
		self.context_menu.add_command(label="Load into Planner", command=self.load_budget)
		self.context_menu.add_command(label="Delete Budget", command=self.delete_budget)

		for variable in [
			self.budget_name_var,
			self.income_amount_var,
			self.income_frequency_var,
			self.savings_amount_var,
			self.savings_frequency_var,
		]:
			variable.trace_add("write", lambda *_args: self.update_calculations())

		self.add_expense_row(name="Rent", amount=1800, frequency="Monthly", trigger_update=False)
		self.add_expense_row(name="Groceries", amount=150, frequency="Weekly", trigger_update=False)
		self.refresh_table()

	def frequency_to_monthly(self, amount, frequency):
		mapping = {
			"Weekly": 52 / 12,
			"Biweekly": 26 / 12,
			"Monthly": 1,
			"Quarterly": 1 / 3,
			"Annually": 1 / 12,
		}
		return amount * mapping.get(frequency, 1)

	def format_currency(self, value):
		return f"${value:,.2f}"

	def add_expense_row(self, name="", amount=0.0, frequency="Monthly", trigger_update=True):
		row_frame = ttk.Frame(self.expenses_rows_frame)
		row_frame.grid(row=len(self.expense_rows), column=0, sticky="ew", pady=2)
		row_frame.columnconfigure(0, weight=1)

		name_var = tk.StringVar(value=name)
		amount_var = tk.DoubleVar(value=amount)
		frequency_var = tk.StringVar(value=frequency if frequency else "Monthly")

		name_entry = ttk.Entry(row_frame, textvariable=name_var, width=28)
		name_entry.grid(row=0, column=0, sticky="w", padx=(0, 8))

		amount_entry = ttk.Entry(row_frame, textvariable=amount_var, width=14)
		amount_entry.grid(row=0, column=1, sticky="w", padx=(0, 8))

		frequency_combo = ttk.Combobox(
			row_frame,
			textvariable=frequency_var,
			values=["Weekly", "Biweekly", "Monthly", "Quarterly", "Annually"],
			width=12,
			state="readonly",
		)
		frequency_combo.grid(row=0, column=2, sticky="w", padx=(0, 8))

		ttk.Button(
			row_frame,
			text="Remove",
			command=lambda row_data=row_frame: self.remove_expense_row_by_frame(row_data),
		).grid(row=0, column=3, sticky="w")

		row_data = {
			"frame": row_frame,
			"name_var": name_var,
			"amount_var": amount_var,
			"frequency_var": frequency_var,
		}
		self.expense_rows.append(row_data)

		name_var.trace_add("write", lambda *_args: self.update_calculations())
		amount_var.trace_add("write", lambda *_args: self.update_calculations())
		frequency_var.trace_add("write", lambda *_args: self.update_calculations())

		if trigger_update:
			self.regrid_expense_rows()
			self.update_calculations()

	def remove_expense_row_by_frame(self, row_frame):
		self.expense_rows = [row for row in self.expense_rows if row["frame"] != row_frame]
		row_frame.destroy()
		self.regrid_expense_rows()
		self.update_calculations()

	def remove_last_expense_row(self):
		if not self.expense_rows:
			return
		last = self.expense_rows.pop()
		last["frame"].destroy()
		self.regrid_expense_rows()
		self.update_calculations()

	def regrid_expense_rows(self):
		for index, row in enumerate(self.expense_rows):
			row["frame"].grid_configure(row=index)

	def get_expenses_data(self):
		expenses = []
		for row in self.expense_rows:
			name = row["name_var"].get().strip()
			try:
				amount = max(float(row["amount_var"].get()), 0.0)
			except (ValueError, tk.TclError):
				amount = 0.0
			frequency = row["frequency_var"].get().strip() or "Monthly"

			if not name and amount == 0:
				continue

			expenses.append(
				{
					"name": name or "Unnamed Expense",
					"amount": amount,
					"frequency": frequency,
				}
			)
		return expenses

	def calculate_metrics(self):
		income_amount = max(float(self.income_amount_var.get()), 0.0)
		income_frequency = self.income_frequency_var.get().strip() or "Monthly"
		savings_amount = max(float(self.savings_amount_var.get()), 0.0)
		savings_frequency = self.savings_frequency_var.get().strip() or "Monthly"

		monthly_income = self.frequency_to_monthly(income_amount, income_frequency)
		yearly_income = monthly_income * 12

		monthly_savings = self.frequency_to_monthly(savings_amount, savings_frequency)
		yearly_savings = monthly_savings * 12

		expenses = self.get_expenses_data()
		monthly_expenses = sum(self.frequency_to_monthly(item["amount"], item["frequency"]) for item in expenses)
		yearly_expenses = monthly_expenses * 12

		monthly_net = monthly_income - monthly_savings - monthly_expenses
		yearly_net = yearly_income - yearly_savings - yearly_expenses

		return {
			"monthly_income": monthly_income,
			"yearly_income": yearly_income,
			"monthly_savings": monthly_savings,
			"yearly_savings": yearly_savings,
			"monthly_expenses": monthly_expenses,
			"yearly_expenses": yearly_expenses,
			"monthly_net": monthly_net,
			"yearly_net": yearly_net,
			"expenses": expenses,
			"income_amount": income_amount,
			"income_frequency": income_frequency,
			"savings_amount": savings_amount,
			"savings_frequency": savings_frequency,
		}

	def update_calculations(self, *_args):
		try:
			metrics = self.calculate_metrics()
		except (ValueError, tk.TclError):
			return

		self.monthly_income_var.set(self.format_currency(metrics["monthly_income"]))
		self.yearly_income_var.set(self.format_currency(metrics["yearly_income"]))
		self.monthly_savings_var.set(self.format_currency(metrics["monthly_savings"]))
		self.yearly_savings_var.set(self.format_currency(metrics["yearly_savings"]))
		self.monthly_expenses_var.set(self.format_currency(metrics["monthly_expenses"]))
		self.yearly_expenses_var.set(self.format_currency(metrics["yearly_expenses"]))
		self.monthly_net_var.set(self.format_currency(metrics["monthly_net"]))
		self.yearly_net_var.set(self.format_currency(metrics["yearly_net"]))

		if metrics["monthly_net"] < 0:
			self.monthly_net_label.configure(foreground="#b71c1c")
		else:
			self.monthly_net_label.configure(foreground="#1b5e20")

		if metrics["yearly_net"] < 0:
			self.yearly_net_label.configure(foreground="#b71c1c")
		else:
			self.yearly_net_label.configure(foreground="#1b5e20")

	def build_budget_record(self):
		budget_name = self.budget_name_var.get().strip()
		if not budget_name:
			raise ValueError("Please enter a budget name.")

		metrics = self.calculate_metrics()
		notes = self.notes_text.get("1.0", tk.END).strip()

		return {
			"Budget Name": budget_name,
			"Income": f"{self.format_currency(metrics['income_amount'])} / {metrics['income_frequency']}",
			"Savings": f"{self.format_currency(metrics['savings_amount'])} / {metrics['savings_frequency']}",
			"Monthly Expenses": self.format_currency(metrics["monthly_expenses"]),
			"Monthly Net": self.format_currency(metrics["monthly_net"]),
			"Yearly Net": self.format_currency(metrics["yearly_net"]),
			"Raw Data": {
				"budget_name": budget_name,
				"income_amount": metrics["income_amount"],
				"income_frequency": metrics["income_frequency"],
				"savings_amount": metrics["savings_amount"],
				"savings_frequency": metrics["savings_frequency"],
				"expenses": metrics["expenses"],
				"notes": notes,
			},
		}

	def add_budget(self):
		try:
			budget_record = self.build_budget_record()
		except (ValueError, tk.TclError) as error:
			messagebox.showwarning("Input Required", str(error))
			return

		budget_name = budget_record["Budget Name"]
		existing_index = next(
			(index for index, saved_budget in enumerate(self.budgets) if saved_budget.get("Budget Name") == budget_name),
			-1,
		)

		if existing_index >= 0:
			self.budgets[existing_index] = budget_record
		else:
			self.budgets.append(budget_record)

		self.save_data()
		self.refresh_table()

	def refresh_table(self):
		for item in self.tree.get_children():
			self.tree.delete(item)

		for budget in self.budgets:
			self.tree.insert(
				"",
				tk.END,
				values=(
					budget.get("Budget Name", ""),
					budget.get("Income", "$0.00 / Monthly"),
					budget.get("Savings", "$0.00 / Monthly"),
					budget.get("Monthly Expenses", "$0.00"),
					budget.get("Monthly Net", "$0.00"),
					budget.get("Yearly Net", "$0.00"),
				),
			)

	def show_context_menu(self, event):
		item = self.tree.identify_row(event.y)
		if item:
			self.tree.selection_set(item)
			self.context_menu.post(event.x_root, event.y_root)

	def on_double_click(self, event):
		item = self.tree.identify_row(event.y)
		if not item:
			return
		self.tree.selection_set(item)
		self.load_budget()

	def delete_budget(self):
		selection = self.tree.selection()
		if not selection:
			return

		item = selection[0]
		budget_name = self.tree.item(item)["values"][0]
		self.budgets = [budget for budget in self.budgets if budget.get("Budget Name") != budget_name]
		self.save_data()
		self.refresh_table()

	def load_budget(self):
		selection = self.tree.selection()
		if not selection:
			return

		item = selection[0]
		budget_name = self.tree.item(item)["values"][0]
		budget = next((saved_budget for saved_budget in self.budgets if saved_budget.get("Budget Name") == budget_name), None)
		if not budget:
			return

		raw_data = budget.get("Raw Data", {})

		self.budget_name_var.set(raw_data.get("budget_name", ""))
		self.income_amount_var.set(raw_data.get("income_amount", 5000))
		self.income_frequency_var.set(raw_data.get("income_frequency", "Monthly"))
		self.savings_amount_var.set(raw_data.get("savings_amount", 500))
		self.savings_frequency_var.set(raw_data.get("savings_frequency", "Monthly"))

		self.notes_text.delete("1.0", tk.END)
		self.notes_text.insert("1.0", raw_data.get("notes", ""))

		for row in self.expense_rows:
			row["frame"].destroy()
		self.expense_rows = []

		expenses = raw_data.get("expenses", [])
		if expenses:
			for expense in expenses:
				self.add_expense_row(
					name=expense.get("name", ""),
					amount=expense.get("amount", 0),
					frequency=expense.get("frequency", "Monthly"),
					trigger_update=False,
				)
		else:
			self.add_expense_row(trigger_update=False)

		self.regrid_expense_rows()
		self.update_calculations()

	def clear_fields(self):
		self.budget_name_var.set("")
		self.income_amount_var.set(5000)
		self.income_frequency_var.set("Monthly")
		self.savings_amount_var.set(500)
		self.savings_frequency_var.set("Monthly")
		self.notes_text.delete("1.0", tk.END)

		for row in self.expense_rows:
			row["frame"].destroy()
		self.expense_rows = []

		self.add_expense_row(name="Rent", amount=1800, frequency="Monthly", trigger_update=False)
		self.add_expense_row(name="Groceries", amount=150, frequency="Weekly", trigger_update=False)
		self.regrid_expense_rows()
		self.update_calculations()


if __name__ == "__main__":
	root = tk.Tk()
	app = BudgetingApp(root)
	root.mainloop()
