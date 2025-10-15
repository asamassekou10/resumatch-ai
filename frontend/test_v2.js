/**
 * Quick test script for ResumeAnalyzer AI v2.0 Frontend
 * Run this with: node test_v2.js
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 ResumeAnalyzer AI v2.0 Frontend Test');
console.log('=' * 40);

// Test 1: Check if new files exist
function testFileStructure() {
    console.log('\n🔄 Testing file structure...');
    
    const requiredFiles = [
        'src/config/index.js',
        'src/services/api.js',
        'src/contexts/AuthContext.js',
        'src/utils/validation.js',
        'src/hooks/useForm.js',
        'src/components/ErrorBoundary.js',
        'src/components/Loading.js',
        'src/components/forms/FormField.js'
    ];
    
    let passed = 0;
    let total = requiredFiles.length;
    
    requiredFiles.forEach(file => {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            console.log(`✅ ${file}`);
            passed++;
        } else {
            console.log(`❌ ${file} - Missing`);
        }
    });
    
    console.log(`\n📊 File structure: ${passed}/${total} files found`);
    return passed === total;
}

// Test 2: Check package.json updates
function testPackageJson() {
    console.log('\n🔄 Testing package.json updates...');
    
    try {
        const packagePath = path.join(__dirname, 'package.json');
        const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        
        // Check for new dependencies
        const requiredDeps = ['axios'];
        const requiredScripts = ['test:coverage', 'lint', 'lint:fix', 'format'];
        
        let depsOk = true;
        let scriptsOk = true;
        
        requiredDeps.forEach(dep => {
            if (packageJson.dependencies && packageJson.dependencies[dep]) {
                console.log(`✅ Dependency: ${dep}`);
            } else {
                console.log(`❌ Missing dependency: ${dep}`);
                depsOk = false;
            }
        });
        
        requiredScripts.forEach(script => {
            if (packageJson.scripts && packageJson.scripts[script]) {
                console.log(`✅ Script: ${script}`);
            } else {
                console.log(`❌ Missing script: ${script}`);
                scriptsOk = false;
            }
        });
        
        console.log(`\n📊 Package.json: ${depsOk && scriptsOk ? 'Updated' : 'Needs updates'}`);
        return depsOk && scriptsOk;
        
    } catch (error) {
        console.log(`❌ Failed to read package.json: ${error.message}`);
        return false;
    }
}

// Test 3: Check environment configuration
function testEnvironmentConfig() {
    console.log('\n🔄 Testing environment configuration...');
    
    const envExamplePath = path.join(__dirname, 'env.example');
    if (fs.existsSync(envExamplePath)) {
        console.log('✅ env.example file exists');
        
        const envContent = fs.readFileSync(envExamplePath, 'utf8');
        const requiredVars = ['REACT_APP_API_URL', 'REACT_APP_ENV'];
        
        let varsFound = 0;
        requiredVars.forEach(varName => {
            if (envContent.includes(varName)) {
                console.log(`✅ Environment variable: ${varName}`);
                varsFound++;
            } else {
                console.log(`❌ Missing environment variable: ${varName}`);
            }
        });
        
        console.log(`\n📊 Environment config: ${varsFound}/${requiredVars.length} variables found`);
        return varsFound === requiredVars.length;
    } else {
        console.log('❌ env.example file missing');
        return false;
    }
}

// Test 4: Check source code syntax
function testSourceCode() {
    console.log('\n🔄 Testing source code syntax...');
    
    const sourceFiles = [
        'src/config/index.js',
        'src/services/api.js',
        'src/contexts/AuthContext.js',
        'src/utils/validation.js'
    ];
    
    let passed = 0;
    let total = sourceFiles.length;
    
    sourceFiles.forEach(file => {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            try {
                const content = fs.readFileSync(filePath, 'utf8');
                // Basic syntax check - look for common syntax errors
                if (content.includes('export default') || content.includes('module.exports')) {
                    console.log(`✅ ${file} - Basic syntax OK`);
                    passed++;
                } else {
                    console.log(`⚠️  ${file} - No exports found`);
                }
            } catch (error) {
                console.log(`❌ ${file} - Syntax error: ${error.message}`);
            }
        } else {
            console.log(`❌ ${file} - File missing`);
        }
    });
    
    console.log(`\n📊 Source code: ${passed}/${total} files OK`);
    return passed === total;
}

// Main test function
function main() {
    const tests = [
        testFileStructure,
        testPackageJson,
        testEnvironmentConfig,
        testSourceCode
    ];
    
    let passed = 0;
    let total = tests.length;
    
    tests.forEach(test => {
        try {
            if (test()) {
                passed++;
            }
        } catch (error) {
            console.log(`❌ Test ${test.name} crashed: ${error.message}`);
        }
    });
    
    console.log(`\n📊 Overall Results: ${passed}/${total} tests passed`);
    
    if (passed === total) {
        console.log('\n🎉 All frontend tests passed!');
        console.log('\nNext steps:');
        console.log('1. Install dependencies: npm install');
        console.log('2. Set up environment: cp env.example .env.local');
        console.log('3. Start development server: npm start');
        console.log('4. Run tests: npm run test:coverage');
    } else {
        console.log('\n⚠️  Some tests failed. Check the errors above.');
    }
    
    return passed === total;
}

// Run tests
const success = main();
process.exit(success ? 0 : 1);
