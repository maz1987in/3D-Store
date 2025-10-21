import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/services/api.service';
import {
  Expense,
  ExpenseCategory,
  CreateExpenseRequest,
  ExpenseApproval,
  ExpenseBudget,
  ExpenseReport
} from '../models/expense.model';
import { PaginatedResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class ExpenseService {
  constructor(private api: ApiService) {}

  /**
   * Create new expense
   */
  createExpense(request: CreateExpenseRequest): Observable<Expense> {
    const formData = new FormData();
    formData.append('amount', request.amount.toString());
    formData.append('category_id', request.category_id);
    formData.append('description', request.description);
    formData.append('expense_date', request.expense_date.toISOString());
    
    if (request.vendor) {
      formData.append('vendor', request.vendor);
    }
    if (request.receipt) {
      formData.append('receipt', request.receipt);
    }
    if (request.notes) {
      formData.append('notes', request.notes);
    }

    return this.api.post<Expense>('expenses', formData);
  }

  /**
   * Get user's expenses
   */
  getExpenses(params?: {
    page?: number;
    limit?: number;
    status?: string;
    category_id?: string;
  }): Observable<PaginatedResponse<Expense>> {
    return this.api.getPaginated<Expense>('expenses', params);
  }

  /**
   * Get expense by ID
   */
  getExpense(id: string): Observable<Expense> {
    return this.api.get<Expense>(`expenses/${id}`);
  }

  /**
   * Update expense
   */
  updateExpense(id: string, data: Partial<Expense>): Observable<Expense> {
    return this.api.put<Expense>(`expenses/${id}`, data);
  }

  /**
   * Delete expense
   */
  deleteExpense(id: string): Observable<void> {
    return this.api.delete<void>(`expenses/${id}`);
  }

  /**
   * Get expense categories
   */
  getCategories(): Observable<ExpenseCategory[]> {
    return this.api.get<ExpenseCategory[]>('expense-categories');
  }

  /**
   * Get category by ID
   */
  getCategory(id: string): Observable<ExpenseCategory> {
    return this.api.get<ExpenseCategory>(`expense-categories/${id}`);
  }

  /**
   * Get expense budgets
   */
  getBudgets(period?: string): Observable<ExpenseBudget[]> {
    return this.api.get<ExpenseBudget[]>('expense-budgets', { period });
  }

  /**
   * Get expense report
   */
  getExpenseReport(startDate: Date, endDate: Date): Observable<ExpenseReport> {
    return this.api.get<ExpenseReport>('expenses/report', {
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString()
    });
  }

  /**
   * Submit expense for approval
   */
  submitForApproval(id: string): Observable<Expense> {
    return this.api.post<Expense>(`expenses/${id}/submit`, {});
  }

  /**
   * Get pending approvals (admin/manager only)
   */
  getPendingApprovals(params?: {
    page?: number;
    limit?: number;
  }): Observable<PaginatedResponse<Expense>> {
    return this.api.getPaginated<Expense>('expenses/pending-approvals', params);
  }

  /**
   * Approve expense (admin/manager only)
   */
  approveExpense(id: string, comments?: string): Observable<ExpenseApproval> {
    return this.api.post<ExpenseApproval>(`expenses/${id}/approve`, { comments });
  }

  /**
   * Reject expense (admin/manager only)
   */
  rejectExpense(id: string, comments: string): Observable<ExpenseApproval> {
    return this.api.post<ExpenseApproval>(`expenses/${id}/reject`, { comments });
  }

  /**
   * Get all expenses (admin only)
   */
  getAllExpenses(params?: {
    page?: number;
    limit?: number;
    status?: string;
    category_id?: string;
    branch_id?: string;
  }): Observable<PaginatedResponse<Expense>> {
    return this.api.getPaginated<Expense>('admin/expenses', params);
  }

  /**
   * Download receipt
   */
  downloadReceipt(id: string): Observable<Blob> {
    return this.api.downloadFile(`expenses/${id}/receipt`);
  }
}

