const { runConfigurableTests } = require('./runner');

// Export for use as a module or run directly
if (require.main === module) {
  // Run tests when file is executed directly
  runConfigurableTests();
}

module.exports = {
  runConfigurableTests
};