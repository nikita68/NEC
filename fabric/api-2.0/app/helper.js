'use strict';

var { Gateway, Wallets } = require('fabric-network');
const path = require('path');
const FabricCAServices = require('fabric-ca-client');
const fs = require('fs');
const yaml = require('js-yaml')

const util = require('util');

let ccp;


const getRegisteredUser = async (username, userOrg, isJson) => {

    console.log(JSON.stringify(Wallets));

    const userOrgUpper = userOrg;
    userOrg = userOrg.toLowerCase();


    const ccpPath = path.resolve(__dirname, '..', 'config', 'connection-' + userOrg + '.yaml');
    const ccpYaml = fs.readFileSync(ccpPath, 'utf8')
    ccp = yaml.load(ccpYaml);

    // Create a new CA client for interacting with the CA.
    const caURL = ccp.certificateAuthorities['ca.' + userOrg + '.example.com'].url;
    const ca = new FabricCAServices(caURL);

    const walletPath = path.join(process.cwd(), 'wallet-' + userOrg);
    const wallet = await Wallets.newFileSystemWallet(walletPath);
    console.log(`Wallet path: ${walletPath}`);

    const userIdentity = await wallet.get(username);
    if (userIdentity) {
        console.log('An identity for the user "user1" already exists in the wallet');
        var response = {
            success: true,
            message: username + ' enrolled Successfully',
        };
        return response
    }

    // Check to see if we've already enrolled the admin user.
    let adminIdentity = await wallet.get('admin');
    if (!adminIdentity) {
        console.log('An identity for the admin user "admin" does not exist in the wallet');
        await enrollAdmin(userOrg, userOrgUpper);
        adminIdentity = await wallet.get('admin');
        console.log("Admin Enrolled Successfully")
    }

    // build a user object for authenticating with the CA
    const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
    const adminUser = await provider.getUserContext(adminIdentity, 'admin');

    // Register the user, enroll the user, and import the new identity into the wallet.
    const secret = await ca.register({ affiliation: userOrg + '.department1', enrollmentID: username, role: 'client' }, adminUser);
    // const secret = await ca.register({ affiliation: 'org1.department1', enrollmentID: username, role: 'client', attrs: [{ name: 'role', value: 'approver', ecert: true }] }, adminUser);

    const enrollment = await ca.enroll({ enrollmentID: username, enrollmentSecret: secret });
    // const enrollment = await ca.enroll({ enrollmentID: username, enrollmentSecret: secret, attr_reqs: [{ name: 'role', optional: false }] });
    const x509Identity = {
        credentials: {
            certificate: enrollment.certificate,
            privateKey: enrollment.key.toBytes(),
        },
        mspId: userOrgUpper + 'MSP',
        type: 'X.509',
    };

    await wallet.put(username, x509Identity);
    console.log('Successfully registered and enrolled admin user "user1" and imported it into the wallet');

    var response = {
        success: true,
        message: username + ' enrolled Successfully',
    };
    return response
}


const enrollAdmin = async (org, orgUpper) => {

    console.log('calling enroll Admin method')

    try {

        const caInfo = ccp.certificateAuthorities['ca.' + org +'.example.com'];
        const caTLSCACerts = caInfo.tlsCACerts.pem; 
        const ca = new FabricCAServices(caInfo.url, { trustedRoots: caTLSCACerts, verify: false }, caInfo.caName);

        // Create a new file system based wallet for managing identities.
        const walletPath = path.join(process.cwd(), 'wallet-' + org);
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);

        // Check to see if we've already enrolled the admin user.
        const identity = await wallet.get('admin');
        if (identity) {
            console.log('An identity for the admin user "admin" already exists in the wallet');
            return;
        }

        // Enroll the admin user, and import the new identity into the wallet.
        const enrollment = await ca.enroll({ enrollmentID: 'admin', enrollmentSecret: 'adminpw' });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: orgUpper + 'MSP',
            type: 'X.509',
        };
        await wallet.put('admin', x509Identity);
        console.log('Successfully enrolled admin user "admin" and imported it into the wallet');

    } catch (error) {
        console.error(`Failed to enroll admin user "admin": ${error}`);
    }


}


exports.getRegisteredUser = getRegisteredUser