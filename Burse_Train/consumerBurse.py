import pika
import sys
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queue_name_list = sys.argv[1:]#seller_stock name or customer_stock name
if len(queue_name_list) != 1:
    sys.stderr.write(" please say seller_name of stock or customer_name of stock %s \n" % sys.argv[0])
    sys.exit(1)
queue_name = queue_name_list[0]

def delete_file_content():
    with open('SellStockInfo.txt','w'): pass

def modify_file(queue_name):
    if 'customer' in queue_name:
        return
    # print("here in modify_file")
    with open('SellStockInfo.txt', 'r+') as f:
        file_list = f.read().splitlines()
        # print(file_list, type(file_list))
        for info in file_list:
            # print(info)
            info_list = info.split(':')
            if info_list[0] == queue_name:
                return
        f.write(queue_name+':0\n') # appending to the file
    f.close()

def start_process(ch, method, properties, body):
    ch.basic_ack(delivery_tag = method.delivery_tag)

    stock_name_list = method.exchange.split('_')
    stock_name = stock_name_list[0]
    queue_name = 'seller'+'_'+stock_name

    decoded_body = body.decode('utf-8')
    decoded_body_list = decoded_body.split(',')
    stock_quantity = decoded_body_list[2]

    # print("ch: {}, method: {}, property: {}, body: {}".format(ch, method, properties, body))

    if method.routing_key == 'seller':

        print("here in seller *****")
        finish = False
        file_list = []
        index = -1

        with open('SellStockInfo.txt', 'r') as f:
            file_list = f.read().splitlines()
            print("here in reading file in seller #### ")
            for info in file_list:
                print("here in this for")
                index += 1
                info_list = info.split(':')
                if info_list[0] == queue_name:
                    print("i found the queue name")
                    file_list[index] = queue_name+':'+stock_quantity
                    break
        f.close()
        print("before delete_file_content in seller")
        delete_file_content()
        print("after delete_file_content in seller")

        with open('SellStockInfo.txt', 'a') as f:
            print("here in appending to list")
            print(file_list)
            for info in file_list:
                f.write(info+'\n')
        f.close()

        while not finish:
            with open('SellStockInfo.txt', 'r') as f:
                    file_list = f.read().splitlines()
                    for info in file_list:
                        info_list = info.split(':')
                        if info_list[0] == queue_name:
                            if int(info_list[1]) == 0:
                                finish = True
                            break
            f.close()
            # time.sleep(1)
        print('{} with email {}, sold {} from {} stock'.format(decoded_body_list[3],decoded_body_list[4],decoded_body_list[2],decoded_body_list[1]))

    if method.routing_key == 'customer':
        
        stock_quantity_copy = stock_quantity
        # meghdary ke customer mikhad bekhare

        print("here in customer ******")
        remain_stock_to_buy = int(stock_quantity_copy)
        # meghdary ke hanooz bayad moonde va bayad bekhare

        remain_stock = 0
        # meghdary ke hanooz az meghdar stock seller feli moonde

        while remain_stock_to_buy > 0:

            file_list = []
            stock_quantity_for_selling = 0
            # meghdary ke dar in lahze baraye sell mojoode

            index = -1

            with open('SellStockInfo.txt', 'r') as f:
                file_list = f.read().splitlines()
                print(file_list)
                for info in file_list:
                    print("here in reading file and index is : {}".format(index,))
                    index += 1 
                    info_list = info.split(':')
                    if info_list[0] == queue_name:
                        stock_quantity_for_selling = int(info_list[1])
                        break
                if int(stock_quantity_copy) > stock_quantity_for_selling:
                    print("here in first if and index is : {}".format(index,))
                    remain_stock_to_buy = int(stock_quantity_copy)-stock_quantity_for_selling
                    stock_quantity_copy = remain_stock_to_buy
                    remain_stock = 0
                    # time.sleep(1)
                else:
                    print("here in second else and index is : {}".format(index, ))
                    remain_stock_to_buy = 0
                    remain_stock = stock_quantity_for_selling-int(stock_quantity_copy)
                file_list[index] = queue_name+':'+str(remain_stock)
            f.close()
            
            print("before delete_file_content in seller")

            delete_file_content()

            print("after delete_file_content in seller")

            with open('SellStockInfo.txt', 'a') as f:
                for info in file_list:
                    f.write(info+'\n')
            f.close()

            time.sleep(2)
        print('{} with email {}, baught {} from {} stock'.format(decoded_body_list[3],decoded_body_list[4],decoded_body_list[2],decoded_body_list[1]))


channel.basic_consume(queue=queue_name, on_message_callback=start_process)

modify_file(queue_name)

channel.start_consuming()

