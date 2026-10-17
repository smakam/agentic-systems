"""Lab-only registration helper; retain the normal five-tool production contract."""
def register_seller_balance(server, ctx):
    @server.tool(structured_output=False)
    def get_seller_balance(seller_id: str) -> dict:
        """Read one seller balance in paise; unpaid does not mean ready to release."""
        return ctx.query(
            'SELECT seller_id, name, captured, refunded, fees, paid_out, unpaid '
            'FROM analytics.seller_balances WHERE seller_id = %(seller_id)s',
            {'seller_id': seller_id}, 'Read one seller balance')
    return get_seller_balance
