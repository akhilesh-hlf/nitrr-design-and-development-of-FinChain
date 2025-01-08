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

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');

const company_names = ['Shardha', 'Rosevalley', 'Amongus', 'Arambh', 'Welcome', 'greatdeal', 'success', 'Growth', 'sri_ram', 'vijay_laxmi'];
const company_types = ['Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Individual', 'Co-operative'];
const ownerregistration_nos = ['CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG12457630', 'CG10457633'];
const PANs = ['1245-8759-84523-7859', '12458759', '12458759', '12458759', '12458759', '12458759', '12458759', '12458759', '12458759', 'ccbps9703b'];

/**
 * Workload module for the benchmark round.
 */
class CreateTxWorkload extends WorkloadModuleBase {
    /**
     * Initializes the workload module instance.
     */
    constructor() {
        super();
        this.txIndex = 0;
    }

    /**
     * Assemble TXs for the round.
     * @return {Promise<TxStatus[]>}
     */
    async submitTransaction() {
        this.txIndex++;
        let TxNumber = 'Client' + this.workerIndex + '_Tx' + this.txIndex.toString();
        let company_name = company_names[Math.floor(Math.random() * company_names.length)];
        let company_type = company_types[Math.floor(Math.random() * company_types.length)];
        let ownerregistration_no = ownerregistration_nos[Math.floor(Math.random() * ownerregistration_nos.length)];
        let PAN = PANs[Math.floor(Math.random() * PANs.length)];

        let args = {
            //contractId: 'fabcargo',
            //contractId: 'fabcarjs',
            contractId: 'Tx',
            contractVersion: 'v1',
            contractFunction: 'createTx',
            contractArguments: [TxNumber, company_type, ownerregistration_no, company_name, PAN],
            timeout: 30
        };

        await this.sutAdapter.sendRequests(args);
    }
}

/**
 * Create a new instance of the workload module.
 * @return {WorkloadModuleInterface}
 */
function createWorkloadModule() {
    return new CreateTxWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule;
