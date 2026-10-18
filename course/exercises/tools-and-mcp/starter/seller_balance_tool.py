"""Complete the seller-balance handler in this isolated lab template."""
def register_seller_balance(server, ctx):
    @server.tool(structured_output=False)
    def get_seller_balance(seller_id: str) -> dict:
        """Read one seller balance in paise; unpaid does not mean ready to release."""
        # TODO: return ctx.query(sql, parameters, purpose).
        # Read seller_id, name, captured, refunded, fees, paid_out, unpaid
        # from analytics.seller_balances for this bound seller_id only.
        raise NotImplementedError('Complete the seller-balance query')
    return get_seller_balance
