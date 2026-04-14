import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const isAuthenticated = !!localStorage.getItem('token');

  if (isAuthenticated) {
    return true;
  } else {
    // Redireciona para o login caso não tenha logado
    return router.parseUrl('/login');
  }
};
