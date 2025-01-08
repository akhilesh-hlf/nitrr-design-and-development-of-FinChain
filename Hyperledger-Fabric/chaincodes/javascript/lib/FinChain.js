/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const { Contract } = require('fabric-contract-api');
var sum1= 0;
var sum2=0;
//var executionTimeMS;
class FinChain extends Contract {
    
    async initLedger(ctx) {
        console.info('============= START : Initialize Transaction Ledger ===========');
        const FinChains = [
            {
                
                Customer_name: 'Mr. AAA SHAAA',
                Father_name: 'Mr. XXXXXX',
                DOB: '01-02-2002',
                Unique_Id: 'CG12457630',
                PAN_Id: '8759-84523-7859',
                Address: 'H.N.-128, AAAA, ZZZZZZ, 495001 ',
                Contact_num:'1234567890',
                hashd: 'a3c7d79ca378c883d56bddcc14263727f9',
            },

                   
        ];

        for (let i = 0; i < FinChains.length; i++) {
            FinChains[i].docType = 'eKYC';
            await ctx.stub.putState('eKYC' + i, Buffer.from(JSON.stringify(FinChains[i])));
            console.info('Added <--> ', FinChains[i]);
        }//result=$
        console.info('============= END : Initialize Ledger ===========');
    }

    async queryTx(ctx, eKYCNumber) {
        var startTime1 = process.hrtime();
        let executionTimeMS1;
        const TxAsBytes = await ctx.stub.getState(eKYCNumber); // get the FinChain records from chaincode state
        if (!TxAsBytes || TxAsBytes.length === 0) {
            throw new Error(`${eKYCNumber} does not exist`);
        }
        console.log(TxAsBytes.toString());
        let endTime1 = process.hrtime(startTime1);
        executionTimeMS1 = (endTime1[0] * 1000 + endTime1[1] / 1000000).toFixed(2);
        sum1 = sum1 + executionTimeMS1+',';
        return ('Total Query Time='+sum1);
        
    }
  

    async verifyKYC(ctx, eKYCNumber, sharedHash) {
        
        const eKYCAsBytes = await ctx.stub.getState(eKYCNumber); // get the FinChain records from chaincode state
        if (!eKYCAsBytes || eKYCAsBytes.length === 0) {
            throw new Error(`${eKYCNumber} does not exist`);
        }
        console.log(eKYCAsBytes.toString());
        
        const customer_encrypted_records = JSON.parse(eKYCAsBytes.toString());
        const Hash_retrieve_blockchain = customer_encrypted_records.hashd;
        
        if( sharedHash == Hash_retrieve_blockchain){
            return("Successfully verified e-KYC record of the hash " + Hash_retrieve_blockchain)
            
        }
        else{
            throw new Error("e-KYC verification failed!!!!!");
        }
        
    }
    
    
    async createTx(ctx, eKYCNumber, Customer_name, Father_name, DOB, Unique_Id, PAN_Id, Address, Contact_num) {  
        console.info('============= START : Create Transaction===========');
        var startTime2 = process.hrtime(); //calculate time

        
        var crypto = require('crypto');
    
        var hashd = 'QmbPapwoiMnTbDC2et8XEBHSH5Vrk5ohbiw7Wxp6WmG7Sh'
        console.log(hashd);
   
        const eKYC = {  
            Customer_name,
            Father_name, 
            DOB, 
            Unique_Id, 
            PAN_Id, 
            Address, 
            Contact_num,
            hashd
        }
        
        await ctx.stub.putState(eKYCNumber, Buffer.from(JSON.stringify(eKYC)));
        
        let endTime2 = process.hrtime(startTime2);
        let executionTimeMs2 = (endTime2[0] * 1000 + endTime2[1] / 1000000).toFixed(2);
        // // return executionTimeMs;
        sum2 = sum2 + executionTimeMs2+',';
        return('Execution Time Create Tx ='+sum2);
        
        console.info('============= END : Create Transaction Process ===========');
        
    }

    async queryAllTxs(ctx) {
        const startKey = '';
        const endKey = '';
        const allResults = [];
        for await (const {key, value} of ctx.stub.getStateByRange(startKey, endKey)) {
            const strValue = Buffer.from(value).toString('utf8');
            let record;
            try {
                record = JSON.parse(strValue);
            } catch (err) {
                console.log(err);
                record = strValue;
            }
            allResults.push({ Key: key, Record: record });
        }
        console.info(allResults);
        return JSON.stringify(allResults);
    }

    async changeTxCompanyType(ctx, eKYCNumber, newCompanyType) {
        console.info('============= START : changeFinChain Company Type ===========');

        const eKYCAsBytes = await ctx.stub.getState(eKYCNumber); // get the FinChain records from chaincode state
        if (!eKYCAsBytes || eKYCAsBytes.length === 0) {
            throw new Error(`${eKYCNumber} does not exist`);
        }
        const eKYC = JSON.parse(eKYCAsBytes.toString());
        eKYC.company_type = newCompanyType;

        await ctx.stub.putState(eKYCNumber, Buffer.from(JSON.stringify(eKYC)));
        console.info('============= END : changeFinChain Company Type ===========');
    }

}

module.exports = FinChain;
