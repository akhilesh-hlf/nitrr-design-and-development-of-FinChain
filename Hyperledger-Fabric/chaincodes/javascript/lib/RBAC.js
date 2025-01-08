/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

const { Contract } = require('fabric-contract-api');
const { performance } = require('perf_hooks');

class Permission {
    constructor(name) {
        this.name = name;
    }
}

class Role {
    constructor(name) {
        this.name = name;
        this.permissions = new Set();
    }

    addPermission(permission) {
        this.permissions.add(permission);
    }

    hasPermission(permission) {
        return this.permissions.has(permission);
    }
}

class User {
    constructor(username) {
        this.username = username;
        this.roles = new Set();
    }

    addRole(role) {
        this.roles.add(role);
    }

    hasPermission(permission) {
        for (let role of this.roles) {
            if (role.hasPermission(permission)) {
                return true;
            }
        }
        return false;
    }
}

class RBACSystem extends Contract {
    constructor() {
        super('RBACSystem');
        this.users = {};
        this.roles = {};
        this.permissionCheckTimes = [];
        this.accessRequests = 0;
        this.failedRequests = 0;
        this.startTime = performance.now();
    }

    async initLedger(ctx) {
        console.info('============= START : Initialize Ledger ===========');
        // Initialize roles and permissions
        const adminRole = new Role('admin');
        const userRole = new Role('user');

        const readPermission = new Permission('read');
        const writePermission = new Permission('write');
        const deletePermission = new Permission('delete');

        adminRole.addPermission(readPermission);
        adminRole.addPermission(writePermission);
        adminRole.addPermission(deletePermission);
        userRole.addPermission(readPermission);

        this.roles['admin'] = adminRole;
        this.roles['user'] = userRole;

        console.info('============= END : Initialize Ledger ===========');
    }

    async addUser (ctx, username) {
        const user = new User(username);
        this.users[username] = user;
        await ctx.stub.putState(username, Buffer.from(JSON.stringify(user)));
    }

    async addRole(ctx, roleName) {
        const role = new Role(roleName);
        this.roles[roleName] = role;
        await ctx.stub.putState(roleName, Buffer.from(JSON.stringify(role)));
    }

    async assignRole(ctx, username, roleName) {
        const userAsBytes = await ctx.stub.getState(username);
        const role = this.roles[roleName];

        if (!userAsBytes || !role) {
            throw new Error(`User  or role does not exist`);
        }

        const user = JSON.parse(userAsBytes.toString());
        user.addRole(role);
        await ctx.stub.putState(username, Buffer.from(JSON.stringify(user)));
    }

    async checkPermission(ctx, username, permissionName) {
        const startTime = performance.now();
        const userAsBytes = await ctx.stub.getState(username);
        const permission = new Permission(permissionName);

        if (!userAsBytes) {
            this.failedRequests += 1;
            throw new Error(`User  ${username} does not exist`);
        }

        const user = JSON.parse(userAsBytes.toString());
        const result = user.hasPermission(permission);

        if (!result) {
            this.failedRequests += 1;
        }

        const endTime = performance.now();
        this.accessRequests += 1;
        this.permissionCheckTimes.push(endTime - startTime);
        return result;
    }

    async getPerformanceMetrics(ctx) {
        const totalChecks = this.permissionCheckTimes.length;
        const avgCheckTime = totalChecks > 0 ? this.permissionCheckTimes.reduce((a, b) => a + b) / totalChecks : 0;
        const elapsedTime = performance.now() - this.startTime;
        const throughput = this.accessRequests / (elapsedTime / 1000) || 0; // requests per second
        const errorRate = this.accessRequests > 0 ? this.failedRequests / this.accessRequests : 0;

        return {
            "Execution Time (milliseconds)": elapsedTime,
            "Average Permission Check Time (ms)": avgCheckTime,
            "Throughput (requests/sec)": throughput,
            "Error Rate (%)": errorRate * 100
        };
    }
}

module.exports = RBACSystem;