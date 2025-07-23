
#from socket import *
#$serverName = 'localhost'
#$serverPort = 12000
#$clientSocket = socket(AF_INET, SOCK_DGRAM)
#message = input('Input lowercase sentence:')
#lientSocket.sendto(message.encode(),(serverName, serverPort))
#modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
#print (modifiedMessage.decode())
#clientSocket.close()

from socket import *
import json

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print ('The Bitcoin is ready to receive')
#while 1:
#    message, clientAddress = serverSocket.recvfrom(2048)
#    modifiedMessage = message.decode().upper()
#    serverSocket.sendto(modifiedMessage.encode(), clientAddress)

users = {
    'A' : {'password': 'A', 'balance': 10}, 
    'B' : {'password': 'B', 'balance': 10}, 
    'C' : {'password': 'C', 'balance': 10}, 
    'D' : {'password': 'D', 'balance': 10}, 
    'X' : {'password': 'X', 'balance': 0} 
}


# store the CONFIRMED transactions here 
transactions = []

def get_user_txs(username):
    return [tx for tx in transactions if tx['payer'] == username or tx['payee1'] == username or tx.get('payee2') == username]

# i created a while loop that will always run, it will just wait for the requests 
while True:
    # recieved a message from a client 
    message, clientAddress = serverSocket.recvfrom(5000)
    try:
        request = json.loads(message.decode())
        req_type = request.get('type')
    except:
        error_response = {'status': 'ERROR'}
        serverSocket.sendto(json.dumps(error_response).encode(), clientAddress)
        continue
    # This part will handle the authentication for the username and password
    if req_type == "AUTH":
        username = request['username']
        password = request['password']
        print(f"Received authentication request from user {username}")
        # Check if user exists and password matches
        if username in users and users[username]['password'] == password:
            print(f"User {username} is authenticated")
            response = {
                 # if authorized allow user 
                'status': 'OK',
                'balance': users[username]['balance'],
                'transactions': get_user_txs(username)
            }
        else:
              # failed log in, if they did not match
            print(f"Authentication failed for user {username}")
            response = {'status': 'FAIL'}
             # Send the response back to the client
        serverSocket.sendto(json.dumps(response).encode(), clientAddress)
         # This part will handle the transactions they want to make after they can logged in 
    elif req_type == "TX":
        tx = request['tx']
        payer = tx['payer']
        amount = tx['amount']
        fee = round(amount * 0.1, 2) # fee they must pay
        print(f"Received transaction from {payer} with ID {tx['tx_id']}")
        # Check if payer has enough balance to make the transaction they want 
        if users[payer]['balance'] < amount:
            print(f"Transaction {tx['tx_id']} rejected due to insufficient funds")
            response = {'status': 'REJECTED', 'balance': users[payer]['balance']}
        else:
            # Subtract the full amount from the payer
            users[payer]['balance'] -= amount
            # Add Payee1's amount
            users[tx['payee1']]['balance'] += tx['amount1']
            # If Payee2's amount if exists, then we also add
            if tx.get('payee2'):
                users[tx['payee2']]['balance'] += tx['amount2']
            # Add fee to account 'X'
            users['X']['balance'] += fee
            transactions.append(tx)
            # Telling the client the confirmation and new balance 
            print(f"Confirmed a transaction for user {payer}")
            response = {'status': 'CONFIRMED', 'balance': users[payer]['balance']}
        serverSocket.sendto(json.dumps(response).encode(), clientAddress)
# This part will allow the request to get the user's transactions
    elif req_type == "GET_TXS":
        username = request['username']
        print(f"Send the list of transactions to user {username}")
        response = {
            'balance': users[username]['balance'],
            'transactions': get_user_txs(username)
        }
        serverSocket.sendto(json.dumps(response).encode(), clientAddress)
 # This one is to do the request of account X's balance
    elif req_type == "GET_X":
        print("Sending X’s balance to client")
        response = {'balance': users['X']['balance']}
        serverSocket.sendto(json.dumps(response).encode(), clientAddress) # send it back to client