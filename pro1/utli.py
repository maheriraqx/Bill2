






def invoiceprint(request, number,comp):
    # Get the Invoice object using the provided number.
    invoice = Invoice.objects.get(invoice_number=number)

    # Get additional data if needed (e.g., agent, items).
    context = {
        'agent': invoice.agent,
        'invoice': invoice,
        'items': invoice.items.all(),
        'comp':comp
    }

    # Render the HTML template with context data.
    html_string = render_to_string('inv.html', context)

    pdf_file_io = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file_io)
    pdf_file_io.seek(0)