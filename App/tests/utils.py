from lxml import html, etree

def get_messages(resp_data):
    """ get flashed messages from response.data
        returns all messages as a string 
    """
    data = html.fromstring(resp_data)
    message_elems = data.xpath('//ul[@class="messages"]/li')
    messages = ''.join([str(etree.tostring(i)) for i in message_elems])
    return messages

    
