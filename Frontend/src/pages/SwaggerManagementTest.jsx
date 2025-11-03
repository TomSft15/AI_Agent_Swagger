/**
 * Test Swagger Management Page
 */
const SwaggerManagementTest = ({ onBack }) => {
  console.log('SwaggerManagement rendered');

  return (
    <div style={{ padding: '20px' }}>
      <button onClick={onBack}>Back to Dashboard</button>
      <h1>Swagger Management (Test)</h1>
      <p>This is a test page</p>
    </div>
  );
};

export default SwaggerManagementTest;
