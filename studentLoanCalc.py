import csv
import json
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk


class StudentLoanApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Student Loan Calculator")
		self.root.geometry("1280x920")

		self.data_file = "Student_loans_data.json"
		self.loans = self.load_data()

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
				json.dump(self.loans, file_handle, indent=4)
		except OSError as error:
			messagebox.showerror("Save Error", f"Could not save student loan data: {error}")

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

		tab_calc = ttk.Frame(notebook)
		tab_portfolio = ttk.Frame(notebook)
		tab_amort = ttk.Frame(notebook)

		notebook.add(tab_calc, text="Calculator")
		notebook.add(tab_portfolio, text="Portfolio Summary")
		notebook.add(tab_amort, text="Amortization")

		main_frame = ttk.Frame(tab_calc, padding="15")
		main_frame.grid(row=0, column=0, sticky="nsew")
		main_frame.columnconfigure(0, weight=1)
		main_frame.columnconfigure(1, weight=1)

		input_frame = ttk.LabelFrame(main_frame, text="Loan Details", padding="15")
		input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

		ttk.Label(input_frame, text="Loan Source / Servicer:").grid(row=0, column=0, sticky=tk.W, pady=5)
		self.source_var = tk.StringVar()
		ttk.Entry(input_frame, textvariable=self.source_var, width=38).grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Loan Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
		self.loan_name_var = tk.StringVar()
		ttk.Entry(input_frame, textvariable=self.loan_name_var, width=38).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Loan Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
		self.loan_type_var = tk.StringVar(value="Federal - Unsubsidized")
		ttk.Combobox(
			input_frame,
			textvariable=self.loan_type_var,
			values=[
				"Federal - Subsidized",
				"Federal - Unsubsidized",
				"Federal - PLUS",
				"Private",
				"Refinanced",
				"Other",
			],
			width=26,
			state="readonly",
		).grid(row=2, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Current Balance ($):").grid(row=3, column=0, sticky=tk.W, pady=5)
		self.balance_var = tk.DoubleVar(value=20000)
		ttk.Entry(input_frame, textvariable=self.balance_var).grid(row=3, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Interest Rate (%):").grid(row=4, column=0, sticky=tk.W, pady=5)
		self.interest_rate_var = tk.DoubleVar(value=6.5)
		ttk.Entry(input_frame, textvariable=self.interest_rate_var).grid(row=4, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Auto-Pay Discount (%):").grid(row=5, column=0, sticky=tk.W, pady=5)
		self.autopay_discount_var = tk.DoubleVar(value=0.25)
		ttk.Entry(input_frame, textvariable=self.autopay_discount_var).grid(row=5, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Repayment Term (Years):").grid(row=6, column=0, sticky=tk.W, pady=5)
		self.term_years_var = tk.IntVar(value=10)
		ttk.Combobox(
			input_frame,
			textvariable=self.term_years_var,
			values=["5", "7", "10", "15", "20", "25", "30"],
			width=18,
		).grid(row=6, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Grace Period (Months):").grid(row=7, column=0, sticky=tk.W, pady=5)
		self.grace_period_var = tk.IntVar(value=0)
		ttk.Entry(input_frame, textvariable=self.grace_period_var).grid(row=7, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Interest Accrues During Grace:").grid(row=8, column=0, sticky=tk.W, pady=5)
		self.grace_interest_var = tk.BooleanVar(value=True)
		ttk.Checkbutton(input_frame, variable=self.grace_interest_var).grid(row=8, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Extra Payment (Monthly $):").grid(row=9, column=0, sticky=tk.W, pady=5)
		self.extra_payment_var = tk.DoubleVar(value=0)
		ttk.Entry(input_frame, textvariable=self.extra_payment_var).grid(row=9, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Origination Fee (%):").grid(row=10, column=0, sticky=tk.W, pady=5)
		self.origination_fee_var = tk.DoubleVar(value=0)
		ttk.Entry(input_frame, textvariable=self.origination_fee_var).grid(row=10, column=1, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Servicer Link:").grid(row=11, column=0, sticky=tk.W, pady=5)
		self.link_var = tk.StringVar()
		ttk.Entry(input_frame, textvariable=self.link_var, width=38).grid(row=11, column=1, columnspan=2, sticky=tk.W, pady=5)

		ttk.Label(input_frame, text="Notes:").grid(row=12, column=0, sticky=tk.NW, pady=5)
		self.notes_text = tk.Text(input_frame, width=35, height=6)
		self.notes_text.grid(row=12, column=1, columnspan=2, sticky=tk.W, pady=5)

		right_frame = ttk.Frame(main_frame)
		right_frame.grid(row=0, column=1, sticky="nsew")
		right_frame.columnconfigure(0, weight=1)

		summary_frame = ttk.LabelFrame(right_frame, text="Loan Summary", padding="15")
		summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

		self.effective_rate_var = tk.StringVar(value="0.00%")
		self.minimum_monthly_var = tk.StringVar(value="$0.00")
		self.planned_monthly_var = tk.StringVar(value="$0.00")
		self.grace_interest_total_var = tk.StringVar(value="$0.00")
		self.total_interest_var = tk.StringVar(value="$0.00")
		self.total_cost_var = tk.StringVar(value="$0.00")
		self.total_payments_var = tk.StringVar(value="0")
		self.origination_cost_var = tk.StringVar(value="$0.00")

		ttk.Label(summary_frame, text="Effective Interest Rate:").grid(row=0, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.effective_rate_var, font=("Helvetica", 12, "bold"), foreground="blue").grid(row=0, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Minimum Monthly Payment:").grid(row=1, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.minimum_monthly_var, font=("Helvetica", 12, "bold")).grid(row=1, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Planned Monthly Payment:").grid(row=2, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.planned_monthly_var, font=("Helvetica", 12, "bold")).grid(row=2, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Grace Period Interest:").grid(row=3, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.grace_interest_total_var).grid(row=3, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Origination Fee Cost:").grid(row=4, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.origination_cost_var).grid(row=4, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Total Interest Paid:").grid(row=5, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.total_interest_var).grid(row=5, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Total Repayment Cost:").grid(row=6, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.total_cost_var, font=("Helvetica", 12, "bold")).grid(row=6, column=1, sticky=tk.E, pady=5)

		ttk.Label(summary_frame, text="Months Until Paid Off:").grid(row=7, column=0, sticky=tk.W, pady=5)
		ttk.Label(summary_frame, textvariable=self.total_payments_var).grid(row=7, column=1, sticky=tk.E, pady=5)

		button_frame = ttk.Frame(right_frame)
		button_frame.grid(row=1, column=0, pady=20)

		ttk.Button(button_frame, text="Save Loan", command=self.add_loan).grid(row=0, column=0, padx=10)
		ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).grid(row=0, column=1, padx=10)
		ttk.Button(button_frame, text="Portfolio Summary", command=lambda: notebook.select(tab_portfolio)).grid(row=0, column=2, padx=10)
		ttk.Button(button_frame, text="Show Amortization", command=lambda: notebook.select(tab_amort)).grid(row=0, column=3, padx=10)

		table_frame = ttk.LabelFrame(main_frame, text="Saved Student Loans", padding="15")
		table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
		table_frame.rowconfigure(0, weight=1)
		table_frame.columnconfigure(0, weight=1)

		columns = ("Source", "Loan Name", "Type", "Balance", "Rate", "Monthly", "Interest", "Total Cost", "Link")
		self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
		for column_name in columns:
			self.tree.heading(column_name, text=column_name)
			width = 110
			if column_name == "Source":
				width = 165
			elif column_name == "Loan Name":
				width = 160
			elif column_name == "Type":
				width = 170
			elif column_name == "Link":
				width = 180
			self.tree.column(column_name, width=width, anchor=tk.CENTER)

		self.tree.grid(row=0, column=0, sticky="nsew")
		tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscrollcommand=tree_scroll.set)
		tree_scroll.grid(row=0, column=1, sticky="ns")

		self.tree.bind("<Button-3>", self.show_context_menu)
		self.tree.bind("<Double-1>", self.on_double_click)

		self.context_menu = tk.Menu(self.root, tearoff=0)
		self.context_menu.add_command(label="Delete Loan", command=self.delete_loan)
		self.context_menu.add_command(label="Load into Calculator", command=self.load_loan)
		self.context_menu.add_command(label="Open Link", command=self.open_link)

		portfolio_frame = ttk.Frame(tab_portfolio, padding="15")
		portfolio_frame.grid(row=0, column=0, sticky="nsew")
		portfolio_frame.columnconfigure(0, weight=1)
		portfolio_frame.rowconfigure(2, weight=1)

		totals_frame = ttk.LabelFrame(portfolio_frame, text="Portfolio Totals", padding="15")
		totals_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

		self.portfolio_balance_var = tk.StringVar(value="$0.00")
		self.portfolio_monthly_var = tk.StringVar(value="$0.00")
		self.portfolio_interest_var = tk.StringVar(value="$0.00")
		self.portfolio_cost_var = tk.StringVar(value="$0.00")
		self.portfolio_count_var = tk.StringVar(value="0")
		self.portfolio_payoff_var = tk.StringVar(value="0")

		ttk.Label(totals_frame, text="Total Current Balance:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
		ttk.Label(totals_frame, textvariable=self.portfolio_balance_var, font=("Helvetica", 11, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

		ttk.Label(totals_frame, text="Combined Monthly Payment:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=4)
		ttk.Label(totals_frame, textvariable=self.portfolio_monthly_var, font=("Helvetica", 11, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=4)

		ttk.Label(totals_frame, text="Projected Interest Paid:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
		ttk.Label(totals_frame, textvariable=self.portfolio_interest_var, font=("Helvetica", 11, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

		ttk.Label(totals_frame, text="Projected Total Cost:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=4)
		ttk.Label(totals_frame, textvariable=self.portfolio_cost_var, font=("Helvetica", 11, "bold")).grid(row=1, column=3, sticky=tk.W, padx=5, pady=4)

		ttk.Label(totals_frame, text="Loan Count:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=4)
		ttk.Label(totals_frame, textvariable=self.portfolio_count_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=4)

		ttk.Label(totals_frame, text="Longest Payoff Timeline (Months):").grid(row=2, column=2, sticky=tk.W, padx=5, pady=4)
		ttk.Label(totals_frame, textvariable=self.portfolio_payoff_var).grid(row=2, column=3, sticky=tk.W, padx=5, pady=4)

		source_frame = ttk.LabelFrame(portfolio_frame, text="Totals by Source", padding="15")
		source_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
		source_frame.columnconfigure(0, weight=1)

		self.source_canvas = tk.Canvas(source_frame, height=280, background="white", highlightthickness=1, highlightbackground="#cfcfcf")
		self.source_canvas.grid(row=0, column=0, sticky="nsew")

		source_columns = ("Source", "Loans", "Balance", "Monthly", "Interest", "Total Cost")
		self.source_tree = ttk.Treeview(portfolio_frame, columns=source_columns, show="headings", height=8)
		for column_name in source_columns:
			self.source_tree.heading(column_name, text=column_name)
			width = 140
			if column_name == "Source":
				width = 180
			self.source_tree.column(column_name, width=width, anchor=tk.CENTER)
		self.source_tree.grid(row=2, column=0, sticky="nsew")

		source_scroll = ttk.Scrollbar(portfolio_frame, orient=tk.VERTICAL, command=self.source_tree.yview)
		self.source_tree.configure(yscrollcommand=source_scroll.set)
		source_scroll.grid(row=2, column=1, sticky="ns")

		amort_frame = ttk.Frame(tab_amort, padding="10")
		amort_frame.grid(row=0, column=0, sticky="nsew")
		amort_frame.columnconfigure(0, weight=1)

		amort_columns = ("Month", "Phase", "Payment", "Principal", "Interest", "Balance")
		self.amort_tree = ttk.Treeview(amort_frame, columns=amort_columns, show="headings", height=20)
		for column_name in amort_columns:
			self.amort_tree.heading(column_name, text=column_name)
			width = 120
			if column_name == "Month":
				width = 70
			elif column_name == "Phase":
				width = 110
			self.amort_tree.column(column_name, width=width, anchor=tk.E)
		self.amort_tree.column("Month", anchor=tk.CENTER)
		self.amort_tree.column("Phase", anchor=tk.CENTER)
		self.amort_tree.grid(row=0, column=0, sticky="nsew")

		amort_scroll = ttk.Scrollbar(amort_frame, orient=tk.VERTICAL, command=self.amort_tree.yview)
		self.amort_tree.configure(yscrollcommand=amort_scroll.set)
		amort_scroll.grid(row=0, column=1, sticky="ns")

		amort_buttons = ttk.Frame(amort_frame)
		amort_buttons.grid(row=1, column=0, sticky="e", pady=8)
		ttk.Button(amort_buttons, text="Export CSV", command=self.export_amortization_csv).grid(row=0, column=0, padx=6)
		ttk.Button(amort_buttons, text="Back to Calculator", command=lambda: notebook.select(tab_calc)).grid(row=0, column=1, padx=6)

		for variable in [
			self.source_var,
			self.loan_name_var,
			self.loan_type_var,
			self.balance_var,
			self.interest_rate_var,
			self.autopay_discount_var,
			self.term_years_var,
			self.grace_period_var,
			self.grace_interest_var,
			self.extra_payment_var,
			self.origination_fee_var,
			self.link_var,
		]:
			variable.trace_add("write", lambda *_args: self.update_calculations())

		self.refresh_table()
		self.refresh_portfolio_summary()
		self.refresh_amortization()

	def format_currency(self, value):
		return f"${value:,.2f}"

	def get_form_data(self):
		return {
			"source": self.source_var.get().strip(),
			"loan_name": self.loan_name_var.get().strip(),
			"loan_type": self.loan_type_var.get().strip(),
			"balance": self.balance_var.get(),
			"interest_rate": self.interest_rate_var.get(),
			"autopay_discount": self.autopay_discount_var.get(),
			"term_years": self.term_years_var.get(),
			"grace_period": self.grace_period_var.get(),
			"grace_interest": self.grace_interest_var.get(),
			"extra_payment": self.extra_payment_var.get(),
			"origination_fee": self.origination_fee_var.get(),
			"link": self.link_var.get().strip(),
			"notes": self.notes_text.get("1.0", tk.END).strip(),
		}

	def calculate_metrics(self, raw_data, include_schedule=False):
		starting_balance = max(float(raw_data.get("balance", 0)), 0.0)
		stated_rate = max(float(raw_data.get("interest_rate", 0)), 0.0)
		autopay_discount = max(float(raw_data.get("autopay_discount", 0)), 0.0)
		term_years = max(int(raw_data.get("term_years", 10)), 1)
		grace_period = max(int(raw_data.get("grace_period", 0)), 0)
		extra_payment = max(float(raw_data.get("extra_payment", 0)), 0.0)
		origination_rate = max(float(raw_data.get("origination_fee", 0)), 0.0)
		accrues_during_grace = bool(raw_data.get("grace_interest", False))

		effective_rate = max(stated_rate - autopay_discount, 0.0)
		monthly_rate = effective_rate / 100.0 / 12.0
		repayment_months = term_years * 12
		origination_cost = starting_balance * (origination_rate / 100.0)

		working_balance = starting_balance
		grace_interest_total = 0.0
		total_interest_paid = 0.0
		schedule = []

		for month in range(1, grace_period + 1):
			interest_charge = working_balance * monthly_rate if accrues_during_grace else 0.0
			if accrues_during_grace:
				working_balance += interest_charge
				grace_interest_total += interest_charge
				total_interest_paid += interest_charge

			if include_schedule:
				schedule.append(
					(
						month,
						"Grace",
						0.0,
						0.0,
						interest_charge,
						round(working_balance, 2),
					)
				)

		if working_balance > 0 and monthly_rate > 0:
			factor = (1 + monthly_rate) ** repayment_months
			minimum_monthly_payment = working_balance * ((monthly_rate * factor) / (factor - 1))
		elif working_balance > 0:
			minimum_monthly_payment = working_balance / repayment_months
		else:
			minimum_monthly_payment = 0.0

		planned_monthly_payment = minimum_monthly_payment + extra_payment if working_balance > 0 else 0.0

		amortization_months = 0
		if working_balance > 0:
			while working_balance > 0.01 and amortization_months < repayment_months + 600:
				amortization_months += 1
				interest_charge = working_balance * monthly_rate
				principal_payment = minimum_monthly_payment - interest_charge
				total_principal_payment = principal_payment + extra_payment

				if total_principal_payment <= 0:
					raise ValueError("The payment setup does not reduce the loan balance.")

				if total_principal_payment > working_balance:
					total_principal_payment = working_balance

				payment_amount = interest_charge + total_principal_payment
				working_balance = max(0.0, working_balance - total_principal_payment)
				total_interest_paid += interest_charge

				if include_schedule:
					schedule.append(
						(
							grace_period + amortization_months,
							"Repayment",
							round(payment_amount, 2),
							round(total_principal_payment, 2),
							round(interest_charge, 2),
							round(working_balance, 2),
						)
					)

		total_months = grace_period + amortization_months
		total_cost = starting_balance + origination_cost + total_interest_paid

		return {
			"effective_rate": effective_rate,
			"minimum_monthly_payment": minimum_monthly_payment,
			"planned_monthly_payment": planned_monthly_payment,
			"grace_interest_total": grace_interest_total,
			"origination_cost": origination_cost,
			"total_interest_paid": total_interest_paid,
			"total_cost": total_cost,
			"total_months": total_months,
			"schedule": schedule,
			"current_balance": starting_balance,
		}

	def update_calculations(self, *_args):
		try:
			metrics = self.calculate_metrics(self.get_form_data())
		except (ValueError, tk.TclError):
			return

		self.effective_rate_var.set(f"{metrics['effective_rate']:.2f}%")
		self.minimum_monthly_var.set(self.format_currency(metrics["minimum_monthly_payment"]))
		self.planned_monthly_var.set(self.format_currency(metrics["planned_monthly_payment"]))
		self.grace_interest_total_var.set(self.format_currency(metrics["grace_interest_total"]))
		self.origination_cost_var.set(self.format_currency(metrics["origination_cost"]))
		self.total_interest_var.set(self.format_currency(metrics["total_interest_paid"]))
		self.total_cost_var.set(self.format_currency(metrics["total_cost"]))
		self.total_payments_var.set(str(metrics["total_months"]))
		self.refresh_amortization()

	def generate_amortization_schedule(self):
		metrics = self.calculate_metrics(self.get_form_data(), include_schedule=True)
		return metrics["schedule"]

	def refresh_amortization(self):
		try:
			rows = self.generate_amortization_schedule()
		except (ValueError, tk.TclError):
			rows = []

		for item in self.amort_tree.get_children():
			self.amort_tree.delete(item)

		for row in rows:
			self.amort_tree.insert(
				"",
				tk.END,
				values=(
					row[0],
					row[1],
					self.format_currency(row[2]),
					self.format_currency(row[3]),
					self.format_currency(row[4]),
					self.format_currency(row[5]),
				),
			)

	def export_amortization_csv(self):
		try:
			rows = self.generate_amortization_schedule()
		except (ValueError, tk.TclError):
			rows = []

		if not rows:
			messagebox.showinfo("No Data", "No amortization data to export.")
			return

		path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
		if not path:
			return

		try:
			with open(path, "w", newline="", encoding="utf-8") as csv_file:
				writer = csv.writer(csv_file)
				writer.writerow(["Month", "Phase", "Payment", "Principal", "Interest", "Balance"])
				writer.writerows(rows)
			messagebox.showinfo("Exported", f"Amortization exported to {path}")
		except OSError as error:
			messagebox.showerror("Export Error", f"Could not export amortization: {error}")

	def build_loan_record(self):
		raw_data = self.get_form_data()
		metrics = self.calculate_metrics(raw_data)

		return {
			"Source": raw_data["source"],
			"Loan Name": raw_data["loan_name"],
			"Type": raw_data["loan_type"],
			"Balance": self.format_currency(metrics["current_balance"]),
			"Rate": f"{metrics['effective_rate']:.2f}%",
			"Monthly": self.format_currency(metrics["planned_monthly_payment"]),
			"Interest": self.format_currency(metrics["total_interest_paid"]),
			"Total Cost": self.format_currency(metrics["total_cost"]),
			"Link": raw_data["link"],
			"Raw Data": raw_data,
		}

	def add_loan(self):
		source = self.source_var.get().strip()
		loan_name = self.loan_name_var.get().strip()

		if not source or not loan_name:
			messagebox.showwarning("Input Required", "Please enter both a loan source and a loan name.")
			return

		try:
			loan_record = self.build_loan_record()
		except (ValueError, tk.TclError) as error:
			messagebox.showerror("Calculation Error", str(error))
			return

		existing_index = next(
			(
				index
				for index, loan in enumerate(self.loans)
				if loan.get("Source") == source and loan.get("Loan Name") == loan_name
			),
			-1,
		)

		if existing_index >= 0:
			self.loans[existing_index] = loan_record
		else:
			self.loans.append(loan_record)

		self.save_data()
		self.refresh_table()
		self.refresh_portfolio_summary()

	def refresh_table(self):
		for item in self.tree.get_children():
			self.tree.delete(item)

		for loan in self.loans:
			self.tree.insert(
				"",
				tk.END,
				values=(
					loan.get("Source", ""),
					loan.get("Loan Name", ""),
					loan.get("Type", ""),
					loan.get("Balance", "$0.00"),
					loan.get("Rate", "0.00%"),
					loan.get("Monthly", "$0.00"),
					loan.get("Interest", "$0.00"),
					loan.get("Total Cost", "$0.00"),
					loan.get("Link", ""),
				),
			)

	def refresh_portfolio_summary(self):
		source_totals = {}
		total_balance = 0.0
		total_monthly = 0.0
		total_interest = 0.0
		total_cost = 0.0
		longest_payoff = 0

		for loan in self.loans:
			raw_data = loan.get("Raw Data", {})
			try:
				metrics = self.calculate_metrics(raw_data)
			except (ValueError, tk.TclError):
				continue

			source = raw_data.get("source", "Unknown") or "Unknown"
			source_totals.setdefault(
				source,
				{
					"loan_count": 0,
					"balance": 0.0,
					"monthly": 0.0,
					"interest": 0.0,
					"total_cost": 0.0,
				},
			)

			source_totals[source]["loan_count"] += 1
			source_totals[source]["balance"] += metrics["current_balance"]
			source_totals[source]["monthly"] += metrics["planned_monthly_payment"]
			source_totals[source]["interest"] += metrics["total_interest_paid"]
			source_totals[source]["total_cost"] += metrics["total_cost"]

			total_balance += metrics["current_balance"]
			total_monthly += metrics["planned_monthly_payment"]
			total_interest += metrics["total_interest_paid"]
			total_cost += metrics["total_cost"]
			longest_payoff = max(longest_payoff, metrics["total_months"])

		self.portfolio_balance_var.set(self.format_currency(total_balance))
		self.portfolio_monthly_var.set(self.format_currency(total_monthly))
		self.portfolio_interest_var.set(self.format_currency(total_interest))
		self.portfolio_cost_var.set(self.format_currency(total_cost))
		self.portfolio_count_var.set(str(len(self.loans)))
		self.portfolio_payoff_var.set(str(longest_payoff))

		for item in self.source_tree.get_children():
			self.source_tree.delete(item)

		for source, totals in sorted(source_totals.items()):
			self.source_tree.insert(
				"",
				tk.END,
				values=(
					source,
					totals["loan_count"],
					self.format_currency(totals["balance"]),
					self.format_currency(totals["monthly"]),
					self.format_currency(totals["interest"]),
					self.format_currency(totals["total_cost"]),
				),
			)

		self.draw_source_chart(source_totals)

	def draw_source_chart(self, source_totals):
		self.source_canvas.delete("all")
		self.source_canvas.update_idletasks()

		width = max(self.source_canvas.winfo_width(), 780)
		height = max(self.source_canvas.winfo_height(), 280)

		if not source_totals:
			self.source_canvas.create_text(
				width / 2,
				height / 2,
				text="Save loans to see portfolio totals by source.",
				fill="#555555",
				font=("Helvetica", 13),
			)
			return

		max_cost = max(totals["total_cost"] for totals in source_totals.values()) or 1.0
		bar_left = 220
		bar_right = width - 40
		usable_width = max(bar_right - bar_left, 200)
		top = 30
		row_height = max(int((height - 60) / max(len(source_totals), 1)), 36)

		self.source_canvas.create_text(20, 12, text="Projected total repayment by source", anchor="w", font=("Helvetica", 12, "bold"))

		for index, (source, totals) in enumerate(sorted(source_totals.items())):
			y1 = top + index * row_height
			y2 = y1 + 22
			bar_width = (totals["total_cost"] / max_cost) * usable_width

			self.source_canvas.create_text(20, y1 + 11, text=source, anchor="w", font=("Helvetica", 10, "bold"))
			self.source_canvas.create_rectangle(bar_left, y1, bar_left + bar_width, y2, fill="#4f81bd", outline="")
			self.source_canvas.create_text(
				bar_left + bar_width + 8,
				y1 + 11,
				text=f"{self.format_currency(totals['total_cost'])}  |  Monthly {self.format_currency(totals['monthly'])}",
				anchor="w",
				font=("Helvetica", 9),
			)

	def show_context_menu(self, event):
		item = self.tree.identify_row(event.y)
		if item:
			self.tree.selection_set(item)
			self.context_menu.post(event.x_root, event.y_root)

	def on_double_click(self, event):
		item = self.tree.identify_row(event.y)
		column = self.tree.identify_column(event.x)
		if not item:
			return

		if column == "#9":
			self.open_link()
			return

		self.tree.selection_set(item)
		self.load_loan()

	def open_link(self):
		selection = self.tree.selection()
		if not selection:
			return

		item = selection[0]
		values = self.tree.item(item)["values"]
		if len(values) > 8:
			link = values[8]
			if link and str(link).startswith("http"):
				webbrowser.open(str(link))
			elif link:
				messagebox.showinfo("Link", f"Invalid URL: {link}")

	def delete_loan(self):
		selection = self.tree.selection()
		if not selection:
			return

		item = selection[0]
		values = self.tree.item(item)["values"]
		source = values[0]
		loan_name = values[1]

		self.loans = [
			loan
			for loan in self.loans
			if not (loan.get("Source") == source and loan.get("Loan Name") == loan_name)
		]
		self.save_data()
		self.refresh_table()
		self.refresh_portfolio_summary()

	def load_loan(self):
		selection = self.tree.selection()
		if not selection:
			return

		item = selection[0]
		source, loan_name = self.tree.item(item)["values"][0:2]
		loan = next(
			(
				saved_loan
				for saved_loan in self.loans
				if saved_loan.get("Source") == source and saved_loan.get("Loan Name") == loan_name
			),
			None,
		)

		if not loan:
			return

		raw_data = loan.get("Raw Data", {})
		self.source_var.set(raw_data.get("source", ""))
		self.loan_name_var.set(raw_data.get("loan_name", ""))
		self.loan_type_var.set(raw_data.get("loan_type", "Federal - Unsubsidized"))
		self.balance_var.set(raw_data.get("balance", 20000))
		self.interest_rate_var.set(raw_data.get("interest_rate", 6.5))
		self.autopay_discount_var.set(raw_data.get("autopay_discount", 0.25))
		self.term_years_var.set(raw_data.get("term_years", 10))
		self.grace_period_var.set(raw_data.get("grace_period", 0))
		self.grace_interest_var.set(raw_data.get("grace_interest", True))
		self.extra_payment_var.set(raw_data.get("extra_payment", 0))
		self.origination_fee_var.set(raw_data.get("origination_fee", 0))
		self.link_var.set(raw_data.get("link", ""))
		self.notes_text.delete("1.0", tk.END)
		self.notes_text.insert("1.0", raw_data.get("notes", ""))
		self.update_calculations()

	def clear_fields(self):
		self.source_var.set("")
		self.loan_name_var.set("")
		self.loan_type_var.set("Federal - Unsubsidized")
		self.balance_var.set(20000)
		self.interest_rate_var.set(6.5)
		self.autopay_discount_var.set(0.25)
		self.term_years_var.set(10)
		self.grace_period_var.set(0)
		self.grace_interest_var.set(True)
		self.extra_payment_var.set(0)
		self.origination_fee_var.set(0)
		self.link_var.set("")
		self.notes_text.delete("1.0", tk.END)
		self.update_calculations()


if __name__ == "__main__":
	root = tk.Tk()
	app = StudentLoanApp(root)
	root.mainloop()
