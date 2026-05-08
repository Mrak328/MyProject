import React from 'react';
import './Footer.css';

const currentYear = new Date().getFullYear();

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <p>© {currentYear} Aviko. Все права защищены.</p>
      </div>
    </footer>
  );
}

export default Footer;