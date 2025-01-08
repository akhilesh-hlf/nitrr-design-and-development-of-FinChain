/*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

'use strict';

let company_names = ['Shardha', 'Rosevalley', 'Amongus', 'Arambh', 'Welcome', 'greatdeal', 'success', 'Growth', 'sri_ram', 'vijay_laxmi'];
let company_types = ['Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Co-operative'];
let ownerregistration_nos = ['CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG10457633'];
let PANs = ['1245-8759-84523-7859', '12458759', '12458759', '12458759', '12458759', '12458759', '12458759', '12458759', '12458759', 'ccbps9703b'];

let TxNumber;
let company_name;
let company_type;
let ownerregistration_no;
let PAN;
let txIndex = 0;

module.exports.createTx = async function (bc, workerIndex, args) {

    while (txIndex < args.assets) {
        txIndex++;
        TxNumber = 'Client' + workerIndex + '_Tx' + txIndex.toString();
        company_name = company_names[Math.floor(Math.random() * company_names.length)];
        company_type = company_types[Math.floor(Math.random() * company_types.length)];
        ownerregistration_no = ownerregistration_nos[Math.floor(Math.random() * ownerregistration_nos.length)];
        PAN = PANs[Math.floor(Math.random() * PANs.length)];

        let myArgs = {
            //contractId: 'fabcargo',
            //contractId: 'fabcarjs',
            contractId: 'Tx',
            contractVersion: 'v1',
            contractFunction: 'createTx',
            contractArguments: [TxNumber, company_type, ownerregistration_no, company_name, PAN],
            timeout: 30
        };

        await bc.sendRequests(myArgs);
    }

};
