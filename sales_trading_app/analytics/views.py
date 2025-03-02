from django.http import HttpResponse
from django.views import View  
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from trading.models import Order
import io
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import Counter

class InvoicePDFView(LoginRequiredMixin, View):  
    def get(self, request, *args, **kwargs):
        user = request.user  
        orders = Order.objects.filter(user=user)  
        today_date = datetime.date.today()

        if not orders:
            return HttpResponse("No orders found for this user.", content_type="text/plain")

        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(f"<b>Invoice Report - {today_date}</b>", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 10))

        user_info = Paragraph(f"<b>User:</b> {user.username} | <b>Date:</b> {today_date}", styles["Normal"])
        elements.append(user_info)
        elements.append(Spacer(1, 20))

        # Table Headers
        data = [
            ["Order ID", "Product", "Type", "Quantity", "Price/Unit", "Total", "Status", "Created At"]
        ]

        # Order Details
        for order in orders:
            data.append([
                order.id,
                order.product.name,
                order.get_order_type_display(),
                order.quantity,
                f"${order.price}",
                f"${order.total_price}",
                order.get_status_display(),
                order.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        # Table Styling
        table = Table(data, colWidths=[60, 80, 60, 50, 60, 60, 80, 90])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # 📊 **Data Analysis**
        total_orders = orders.count()
        total_spent = sum(order.total_price for order in orders if order.order_type == "BUY")
        total_earned = sum(order.total_price for order in orders if order.order_type == "SELL")
        
        # Order Status Breakdown
        status_counts = Counter(orders.values_list("status", flat=True))
        pending_count = status_counts.get("PENDING", 0)
        fulfilled_count = status_counts.get("FULFILLED", 0)
        cancelled_count = status_counts.get("CANCELLED", 0)

        # Most Traded Product
        product_counts = Counter(order.product.name for order in orders)
        most_traded_product = product_counts.most_common(1)[0][0] if product_counts else "N/A"

        # **Summary Section**
        summary_data = [
            ["Total Orders", total_orders],
            ["Total Spent (Buy Orders)", f"${total_spent}"],
            ["Total Earned (Sell Orders)", f"${total_earned}"],
            ["Most Traded Product", most_traded_product],
            ["Pending Orders", pending_count],
            ["Fulfilled Orders", fulfilled_count],
            ["Cancelled Orders", cancelled_count],
        ]

        summary_table = Table(summary_data, colWidths=[200, 200])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(Paragraph("<b>Order Analysis Summary</b>", styles["Heading2"]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))

        pdf.build(elements)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice_{user.username}_{today_date}.pdf"'
        return response
