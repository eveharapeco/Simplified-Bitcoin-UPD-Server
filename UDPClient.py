from socket import *
import json
# setting up the client socket using UDP
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

# ----------------------- AUTHENTICATION --------------------------------
# will ask user for username and password 
# usernames that will work are : A, B, C, D, X (password is the same as the username)
while True:
    username = input("Enter username: ")
    password = input("Enter password: ")
    # prepare authentication request
    request = {"type": "AUTH", "username": username, "password": password}
    # send the login request to the UPDServer
    clientSocket.sendto(json.dumps(request).encode(), (serverName, serverPort))
    # this wil recieve the server response
    response, _ = clientSocket.recvfrom(4096)
    try:
        data = json.loads(response.decode())
    except json.JSONDecodeError:
        print("Received invalid response from server.")
        continue # if the decode fails we will ask again 
    if data['status'] == "OK":
        # log in is successful 
        print(f"\nAuthenticated! Your balance: {data['balance']} BTC")
        txs = data['transactions']
        balance = data['balance']
        break
    else:
        # failed log in 
        print("Authentication failed.")
        choice = input("1. Try again\n2. Quit\n> ")
        if choice == '2':
            exit()
        # this will start to tack the transaction IDs for every user 
tx_start_id = {'A': 100, 'B': 200, 'C': 300, 'D': 400}
# ----------MAIN MENU---------
# display menu options
while True:
    print("\nOptions:")
    print("1. Make a transaction")
    print("2. View my transactions")
    print("3. View X's balance")
    print("4. Quit")
    choice = input("> ")
    # -----------------------------------OPTION 1-----------------------------------
    # MAKING A TRANSACTION OPTION
    if choice == "1":
        amount = float(input("How much do you transfer? "))
        # pick the person you want to pay
        others = [u for u in ['A', 'B', 'C', 'D'] if u != username]
        print("Select Payee1:", ", ".join(others))
        p1 = input("Payee1: ")
        # the first person who is getting paid can recieve 90% of the transaction amount 
        max_amt1 = round(amount * 0.9, 2)
        a1 = float(input(f"Amount to {p1} (max {max_amt1}): "))
        while a1 > max_amt1:
            print("Too much. Try again.")
            a1 = float(input(f"Amount to {p1} (max {max_amt1}): "))
            # preparing the transaction history
        tx = {
            'tx_id': tx_start_id[username] + len([t for t in txs if t['payer'] == username]),
            'payer': username,
            'amount': amount,
            'payee1': p1,
            'amount1': a1
        }
        # this is for the scenerio that there is enough left over to send to a second person
        if a1 < max_amt1:
            remaining = round(amount - a1 - amount * 0.1, 2)
            second_choices = [u for u in others if u != p1]
            print("Select Payee2:", ", ".join(second_choices))
            p2 = input("Payee2: ")
            tx['payee2'] = p2
            tx['amount2'] = remaining
            print(f"{p2} will receive {remaining} BTC")
        # add this transaction to the list
        temp_tx = tx.copy()
        temp_tx['status'] = 'temporary'
        txs.append(temp_tx)
        # send this transaction to the server
        request = {'type': 'TX', 'tx': tx}
        clientSocket.sendto(json.dumps(request).encode(), (serverName, serverPort))
        # recieve the response 
        response, _ = clientSocket.recvfrom(4096)
        result = json.loads(response.decode())
        if result['status'] == 'CONFIRMED':
            print("Transaction confirmed.")
            balance = result['balance']
            txs[-1]['status'] = 'confirmed'
        else:
            print("Transaction rejected.")
            txs.pop()
        print(f"Current balance: {balance} BTC")
   # -----------------------------------OPTION 2-----------------------------------
    elif choice == "2":
        # ask for the transactin history from the server
        request = {'type': 'GET_TXS', 'username': username}
        clientSocket.sendto(json.dumps(request).encode(), (serverName, serverPort))
        response, _ = clientSocket.recvfrom(4096)
        data = json.loads(response.decode())
        balance = data['balance']
        txs = data['transactions']
        print(f"Your current balance: {balance} BTC")
        if not txs:
            print("No transactions yet.")
        else:
            # print header 
            headers = ["TX ID", "Payer", "Amt", "Payee1", "Amt1", "Payee2", "Amt2"]
            print("{:<6} {:<6} {:<5} {:<7} {:<6} {:<7} {:<6}".format(*headers))
            for t in txs:
                print("{:<6} {:<6} {:<5} {:<7} {:<6} {:<7} {:<6}".format(
                    t['tx_id'], t['payer'], t['amount'], t['payee1'], t['amount1'],
                    t.get('payee2', '-'), t.get('amount2', '-')
                ))
    # -----------------------------------OPTION 3-----------------------------------
    elif choice == "3":
        request = {'type': 'GET_X'}
        clientSocket.sendto(json.dumps(request).encode(), (serverName, serverPort))
        response, _ = clientSocket.recvfrom(4096)
        data = json.loads(response.decode())
        print(f"X's balance: {data['balance']} BTC")
    # -----------------------------------OPTION 4-----------------------------------
    elif choice == "4":
        break
    else:
        # in case user puts option that is not 1-4
        print("Invalid option.") 




