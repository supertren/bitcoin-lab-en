#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Bitcoin Laboratory
------------------------
This script demonstrates basic Bitcoin operations using the 'bit' library.
It includes address generation, balance checking, and transaction simulation.
"""

import bit
from bit import Key
from bit.network import get_fee_cached
from bit.format import bytes_to_wif
import os
import secrets
import requests

def generate_private_key():
    """Generates a random private key for Bitcoin."""
    # Generate 32 random bytes (256 bits) of entropy
    entropy = secrets.token_bytes(32)
    # Convert bytes to WIF (Wallet Import Format)
    private_key_wif = bytes_to_wif(entropy, compressed=True)
    return private_key_wif

def create_wallet():
    """Creates a new Bitcoin wallet."""
    private_key = generate_private_key()
    wallet = Key(private_key)
    return {
        'private_key': wallet.to_wif(),
        'address': wallet.address,
        'format': 'P2PKH (Legacy)'
    }

def create_segwit_wallet():
    """Creates a new SegWit Bitcoin wallet."""
    private_key = generate_private_key()
    wallet = bit.SegWitKey.from_wif(Key(private_key).to_wif())
    return {
        'private_key': wallet.to_wif(),
        'address': wallet.segwit_address,
        'format': 'P2SH-P2WPKH (SegWit)'
    }

def get_balance(address):
    """Gets the balance of a Bitcoin address in satoshis."""
    try:
        return bit.network.get_balance(address)
    except Exception as e:
        return f"Error getting balance: {e}"

def get_transaction_history(address):
    """Gets the transaction history of a Bitcoin address."""
    try:
        return bit.network.get_transactions(address)
    except Exception as e:
        return f"Error getting transaction history: {e}"

def estimate_fee():
    """Estimates the current Bitcoin network fee in satoshis/byte."""
    try:
        return get_fee_cached()
    except Exception as e:
        return f"Error estimating fee: {e}"

def get_bitcoin_price():
    """Gets the current Bitcoin price in USD."""
    try:
        response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/USD.json')
        data = response.json()
        return float(data['bpi']['USD']['rate'].replace(',', ''))
    except Exception as e:
        return f"Error getting price: {e}"

def simulate_transaction(source_wif, destination_address, amount_btc):
    """Simulates a Bitcoin transaction (without actually sending it)."""
    try:
        wallet = Key(source_wif)
        tx_hex = wallet.create_transaction(
            [(destination_address, amount_btc, 'btc')],
            fee=estimate_fee(),
            absolute_fee=True,
            message='Test transaction from Bitcoin Laboratory'
        )
        return {
            'source': wallet.address,
            'destination': destination_address,
            'amount_btc': amount_btc,
            'tx_hex': tx_hex
        }
    except Exception as e:
        return f"Error creating transaction: {e}"

def show_menu():
    """Displays the main menu of the laboratory."""
    print("\n===== BITCOIN LABORATORY =====")
    print("1. Create new Bitcoin wallet (Legacy)")
    print("2. Create new Bitcoin wallet (SegWit)")
    print("3. Check address balance")
    print("4. Check transaction history")
    print("5. Estimate current network fee")
    print("6. Check current Bitcoin price")
    print("7. Simulate transaction")
    print("0. Exit")
    print("==============================")

def main():
    """Main function of the laboratory."""
    wallets = []
    
    while True:
        show_menu()
        option = input("\nSelect an option: ")
        
        if option == "1":
            new_wallet = create_wallet()
            wallets.append(new_wallet)
            print("\n--- NEW WALLET CREATED (LEGACY) ---")
            print(f"Address: {new_wallet['address']}")
            print(f"Private key (WIF): {new_wallet['private_key']}")
            print("IMPORTANT: Save your private key in a secure place!")
            
        elif option == "2":
            new_wallet = create_segwit_wallet()
            wallets.append(new_wallet)
            print("\n--- NEW WALLET CREATED (SEGWIT) ---")
            print(f"Address: {new_wallet['address']}")
            print(f"Private key (WIF): {new_wallet['private_key']}")
            print("IMPORTANT: Save your private key in a secure place!")
            
        elif option == "3":
            address = input("Enter Bitcoin address: ")
            balance = get_balance(address)
            if isinstance(balance, int):
                print(f"\nBalance: {balance} satoshis ({balance/100000000:.8f} BTC)")
            else:
                print(balance)
                
        elif option == "4":
            address = input("Enter Bitcoin address: ")
            transactions = get_transaction_history(address)
            if isinstance(transactions, list):
                print(f"\nTransaction history for {address}:")
                for i, tx in enumerate(transactions, 1):
                    print(f"{i}. TxID: {tx}")
            else:
                print(transactions)
                
        elif option == "5":
            fee = estimate_fee()
            if isinstance(fee, int):
                print(f"\nEstimated fee: {fee} satoshis/byte")
            else:
                print(fee)
                
        elif option == "6":
            price = get_bitcoin_price()
            if isinstance(price, float):
                print(f"\nCurrent Bitcoin price: ${price:,.2f} USD")
            else:
                print(price)
                
        elif option == "7":
            if not wallets:
                print("\nYou must create at least one wallet first (option 1 or 2).")
                continue
                
            print("\nAvailable wallets:")
            for i, wallet in enumerate(wallets, 1):
                print(f"{i}. {wallet['address']} ({wallet['format']})")
                
            try:
                index = int(input("\nSelect source wallet (number): ")) - 1
                if index < 0 or index >= len(wallets):
                    print("Invalid selection.")
                    continue
                    
                source_wif = wallets[index]['private_key']
                destination = input("Enter destination address: ")
                amount = float(input("Enter amount in BTC: "))
                
                result = simulate_transaction(source_wif, destination, amount)
                if isinstance(result, dict):
                    print("\n--- TRANSACTION SIMULATION ---")
                    print(f"Source: {result['source']}")
                    print(f"Destination: {result['destination']}")
                    print(f"Amount: {result['amount_btc']} BTC")
                    print(f"Transaction hex: {result['tx_hex'][:64]}...")
                    print("NOTE: This is just a simulation, no actual transaction has been sent.")
                else:
                    print(result)
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                
        elif option == "0":
            print("\nThank you for using the Bitcoin Laboratory. Goodbye!")
            break
            
        else:
            print("\nInvalid option. Please select a valid option.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
