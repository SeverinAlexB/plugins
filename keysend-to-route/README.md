# keysend-to-route

This plugin sends a keysend amount to a specific route.

Retrieve route with `getroute`.
```bash
> lightning-cli getroute destination_node amount_msat riskfactor
```

For example:
```bash
> lightning-cli getroute 02ac77f9f7397a64861b573c9e8b8652ce2e67a05150fd166831e9fc167670dfd8 1000 10
```

Send payment with `keysend-to-route`.
```bash
> lightning-cli keysend-to-route '[{"id":"0303a518845db99994783f606e6629e705cfaf072e5ce9a4d8bf9e249de4fbd019","channel":"696348x863x0","direction":1,"msatoshi":2009,"amount_msat":"2009msat","delay":114,"style":"tlv"},{"id":"02bb24da3d0fb0793f4918c7599f973cc402f0912ec3fb530470f1fc08bdd6ecb5","channel":"574084x2137x1","direction":1,"msatoshi":2007,"amount_msat":"2007msat","delay":96,"style":"tlv"},{"id":"02aac548b877279c30f3abbb7301de93096e3b87144fc484dc3409bb0d6bd566b1","channel":"610471x2736x0","direction":1,"msatoshi":2005,"amount_msat":"2005msat","delay":56,"style":"tlv"},{"id":"02ac77f9f7397a64861b573c9e8b8652ce2e67a05150fd166831e9fc167670dfd8","channel":"700310x1616x1","direction":0,"msatoshi":1000,"amount_msat":"1000msat","delay":22,"style":"tlv"}]'
```