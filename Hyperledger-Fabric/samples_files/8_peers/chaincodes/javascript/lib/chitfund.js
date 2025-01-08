/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const { Contract } = require('fabric-contract-api');

class ChitFund extends Contract {

    async initLedger(ctx) {
        console.info('============= START : Initialize Chit Fund Ledger ===========');
        const chits = [
            {
                company_name: 'Shardha',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '1245-8759-84523-7859',
            },
            {
                company_name: 'Rosevalley',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'Amongus',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'Arambh',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'Welcome',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'greatdeal',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'success',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'Growth',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'sri_ram',
                company_type: 'Individual',
                ownerregistration_no: 'CG12457630',
                PAN: '12458759',
            },
            {
                company_name: 'vijay_laxmi',
                company_type: 'Co-operative',
                ownerregistration_no: 'CG10457633',
                PAN: 'ccbps9703b',
            },
        ];

        for (let i = 0; i < chits.length; i++) {
            chits[i].docType = 'chit';
            await ctx.stub.putState('CHIT' + i, Buffer.from(JSON.stringify(chits[i])));
            console.info('Added <--> ', chits[i]);
        }
        console.info('============= END : Initialize Ledger ===========');
    }

    async queryChit(ctx, chitNumber) {
        const chitAsBytes = await ctx.stub.getState(chitNumber); // get the chitfund records from chaincode state
        if (!chitAsBytes || chitAsBytes.length === 0) {
            throw new Error(`${chitNumber} does not exist`);
        }
        console.log(chitAsBytes.toString());
        return chitAsBytes.toString();
    }

    async createChit(ctx, chitNumber, company_name, company_type, ownerregistration_no, PAN) {
        console.info('============= START : Create Chit Fund ===========');

        const chit = {
            company_name,
            docType: 'chit',
            company_type,
            ownerregistration_no,
            PAN,
        };

        await ctx.stub.putState(chitNumber, Buffer.from(JSON.stringify(chit)));
        console.info('============= END : Create Chit Fund Process ===========');
    }

    async queryAllChits(ctx) {
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

    async changeChitCompanyType(ctx, chitNumber, newCompanyType) {
        console.info('============= START : changeChitFund Company Type ===========');

        const chitAsBytes = await ctx.stub.getState(chitNumber); // get the Chitfund records from chaincode state
        if (!chitAsBytes || chitAsBytes.length === 0) {
            throw new Error(`${chitNumber} does not exist`);
        }
        const chit = JSON.parse(chitAsBytes.toString());
        chit.company_type = newCompanyType;

        await ctx.stub.putState(chitNumber, Buffer.from(JSON.stringify(chit)));
        console.info('============= END : changeChitFund Company Type ===========');
    }

}

module.exports = ChitFund;
