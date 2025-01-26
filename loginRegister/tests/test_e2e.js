describe('Chatbot End-to-End Tests', () => {
    it('Visits the chatbot and interacts with it', () => {
        cy.visit('http://localhost:5000')
        cy.get('input[name="email"]').type('test@example.com')
        cy.get('input[name="password"]').type('Qaz_123')
        cy.get('button').click()
        cy.url().should('include', '/index')
        cy.get('input[name="message"]').type('What are the symptoms of COVID-19?')
        cy.get('button').click()
        cy.get('.chatbot-response').should('contain', 'symptoms')
    })
})