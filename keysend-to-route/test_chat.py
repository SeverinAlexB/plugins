from keysend_to_route import keysend_to_route

route = [{"id":"02dfdcca40725ca204eec5d43a9201ff13fcd057c369c058ce4f19e5c178da09f3","channel":"693998x1139x0","direction":1,"msatoshi":6001,"amount_msat":"6001msat","delay":58,"style":"tlv"},{"id":"035352d5960c7f86263e079f29707144088709332e781246b306370ca7e0a64183","channel":"693777x2877x0","direction":0,"msatoshi":1000,"amount_msat":"1000msat","delay":18,"style":"tlv"}]

def test_sendmsg_success():
    keysend_to_route(route, is_test=True)
