from brownie import Lottery, interface, VRFCoordinatorV2Mock
import scripts.helpful_scripts as helpful_scripts
from brownie.network.gas.strategies import GasNowStrategy
from brownie.network import gas_price



class Lottery_class:
    def __init__(self, account = None):
        account = account if account else helpful_scripts.get_account()
        self.gas_strategy = GasNowStrategy("fast")

        self._price_feed = helpful_scripts.get_price_feed_address()

        self.vrf_coordinator2 = helpful_scripts.get_vrf_coordinator2_contract()
        self.key_hash = helpful_scripts.get_key_hash()
        #self.subscriptionId = helpful_scripts.get_subscriptionId()
        self.requestConfirmations = helpful_scripts.get_requestConfirmations()
        self.callbackGasLimit = helpful_scripts.get_callbackGasLimit()
        self.numWords = helpful_scripts.get_numWords()

        self.link = helpful_scripts.get_link_contract()

        self.publish_source = helpful_scripts.get_publish_source()
        
        self.lottery = Lottery.deploy(self._price_feed,
                                      self.vrf_coordinator2.address,
                                      self.key_hash,
                                      #self.subscriptionId,
                                      self.requestConfirmations,
                                      self.callbackGasLimit,
                                      self.numWords,
                                      self.link.address, 
                                      {"from": account},
                                      publish_source=self.publish_source)
        
        
        print("address:", self.lottery.address)
        self.subscriptionId = self.lottery.getSubscriptionId()
        print(self.subscriptionId)
        print("subscripton:", self.vrf_coordinator2.getSubscription(self.subscriptionId))

    def request_random_number(self, account = None):
        account = account if account else helpful_scripts.get_account()
        tx = self.lottery.generateRandomNumber( {"from" : account})
        if (helpful_scripts.get_network() in helpful_scripts.ACTIVE_NETWORKS):
            tx.wait(5)
            return
        requestId = self.lottery.getRequestId()
        tx = self.vrf_coordinator2.fulfillRandomWords(requestId, self.lottery.address, {"from": account})
        

    def cancel_subscription(self, account = None):
        account = account if account else helpful_scripts.get_account()
        tx = self.lottery.cancelSubscription({"from" : account})
        if (helpful_scripts.get_network() in helpful_scripts.ACTIVE_NETWORKS):
            tx.wait(5)
        

    def fund_with_link(self, amount, account = None):
        account = account if account else helpful_scripts.get_account()
        if (helpful_scripts.get_network() not in helpful_scripts.ACTIVE_NETWORKS):
            self.vrf_coordinator2.fundSubscription(self.subscriptionId, amount)
            return
        tx = self.link.approve(self.lottery.address, amount, {"from" : account})
        tx.wait(5)
        print("approved")
        tx = self.link.transfer(self.lottery.address, amount, {"from" : account})
        tx.wait(5)
        print("contract funded")
        tx = self.lottery.topUpSubscription(amount, {"from" : account})
        tx.wait(5)




#gas_price(gas_strategy)


def main():
    lottery = Lottery_class()
    print("random number:", lottery.lottery.getLastRandomNumber())
    print("price:", lottery.lottery.getPriceOfEth())
    print("fee:", lottery.lottery.getFeeInEthWei())
    input()
    lottery.fund_with_link(20*(10**18))
    print("subscripton:", lottery.vrf_coordinator2.getSubscription(lottery.subscriptionId))
    input()
    lottery.request_random_number()
    print("random number:", lottery.lottery.getLastRandomNumber())
    print("subscripton:", lottery.vrf_coordinator2.getSubscription(lottery.subscriptionId))
    input()
    lottery.cancel_subscription()
    #print("subscripton:", lottery.vrf_coordinator2.getSubscription(lottery.subscriptionId))
    #print("random number:", lottery.request_random_number())
