/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';


const FinChain = require('./lib/FinChain');
const RBAC = require('./lib/RBAC');

module.exports.FinChain = FinChain;
module.exports.RBAC = RBAC;
module.exports.contracts = [ FinChain, RBAC  ];
