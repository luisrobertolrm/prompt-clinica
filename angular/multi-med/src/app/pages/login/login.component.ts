import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  
  constructor(private router: Router) {}

  doLogin() {
    // Simula Autenticação
    localStorage.setItem('token', 'jwt_simulado_multi_med_123');
    // Roteia pro sistema interno que iniciará na dashboard
    this.router.navigate(['/dashboard']);
  }
}
