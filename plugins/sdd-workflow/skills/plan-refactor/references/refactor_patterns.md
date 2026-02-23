# Refactoring Patterns Reference

This document provides a catalog of common refactoring patterns referenced by the `/plan-refactor` skill.

## Table of Contents

1. [Extract Interface](#extract-interface)
2. [Extract Class](#extract-class)
3. [Introduce Dependency Injection](#introduce-dependency-injection)
4. [Replace Conditional with Polymorphism](#replace-conditional-with-polymorphism)
5. [Extract Method](#extract-method)
6. [Introduce Parameter Object](#introduce-parameter-object)
7. [Strangler Fig Pattern (for gradual migration)](#strangler-fig-pattern)

---

## Extract Interface

**When to use:**
- You have a class with multiple responsibilities
- You want to enable testing with mocks
- You need to swap implementations

**Steps:**
1. Identify the public methods to extract
2. Create an interface with those methods
3. Make the existing class implement the interface
4. Update client code to depend on the interface, not the concrete class

**Example:**

Before:
```typescript
class EmailService {
  send(to: string, subject: string, body: string): void {
    // SMTP logic...
  }
}

class UserController {
  private emailService = new EmailService();  // Hard dependency

  async sendWelcomeEmail(user: User) {
    this.emailService.send(user.email, "Welcome", "...");
  }
}
```

After:
```typescript
interface IEmailService {
  send(to: string, subject: string, body: string): void;
}

class SmtpEmailService implements IEmailService {
  send(to: string, subject: string, body: string): void {
    // SMTP logic...
  }
}

class UserController {
  constructor(private emailService: IEmailService) {}  // Injected dependency

  async sendWelcomeEmail(user: User) {
    this.emailService.send(user.email, "Welcome", "...");
  }
}
```

**Benefits:**
- Testable (can inject mock)
- Flexible (can swap implementations)
- Follows Dependency Inversion Principle

---

## Extract Class

**When to use:**
- A class has too many responsibilities (violates Single Responsibility Principle)
- Part of the class changes for different reasons than the rest

**Steps:**
1. Identify cohesive group of fields and methods
2. Create a new class to hold them
3. Move fields and methods to the new class
4. Replace old references with delegation to new class

**Example:**

Before:
```typescript
class User {
  id: string;
  name: string;
  email: string;

  // Address fields mixed in
  street: string;
  city: string;
  zipCode: string;

  validateEmail(): boolean { /*...*/ }
  validateAddress(): boolean { /*...*/ }
}
```

After:
```typescript
class Address {
  constructor(
    public street: string,
    public city: string,
    public zipCode: string
  ) {}

  validate(): boolean { /*...*/ }
}

class User {
  constructor(
    public id: string,
    public name: string,
    public email: string,
    public address: Address
  ) {}

  validateEmail(): boolean { /*...*/ }
}
```

**Benefits:**
- Each class has a single responsibility
- Easier to understand and maintain
- Address can be reused elsewhere

---

## Introduce Dependency Injection

**When to use:**
- Hard-coded dependencies make testing difficult
- You want to enable configuration flexibility
- You need to swap implementations at runtime

**Steps:**
1. Identify hard-coded dependencies (e.g., `new SomeClass()` in constructor)
2. Add constructor parameters for those dependencies
3. Update instantiation sites to pass dependencies
4. (Optional) Use DI framework (e.g., InversifyJS, tsyringe)

**Example:**

Before:
```typescript
class OrderService {
  private db = new PostgresDatabase();  // Hard-coded
  private email = new EmailService();   // Hard-coded

  async createOrder(order: Order) {
    await this.db.save(order);
    await this.email.send(...);
  }
}
```

After:
```typescript
class OrderService {
  constructor(
    private db: IDatabase,
    private email: IEmailService
  ) {}

  async createOrder(order: Order) {
    await this.db.save(order);
    await this.email.send(...);
  }
}

// In main.ts (composition root)
const db = new PostgresDatabase();
const email = new SmtpEmailService();
const orderService = new OrderService(db, email);
```

**Benefits:**
- Fully testable (inject mocks)
- Configuration flexibility
- Clear dependencies

---

## Replace Conditional with Polymorphism

**When to use:**
- You have large if/else or switch statements based on type
- Behavior varies by type
- Adding new types requires modifying existing code

**Steps:**
1. Create an interface or base class
2. Create subclasses for each type
3. Move type-specific logic into subclasses
4. Replace conditional with polymorphic call

**Example:**

Before:
```typescript
function calculateDiscount(user: User): number {
  if (user.type === "premium") {
    return user.totalPurchases * 0.2;
  } else if (user.type === "regular") {
    return user.totalPurchases * 0.1;
  } else {
    return 0;
  }
}
```

After:
```typescript
interface User {
  calculateDiscount(): number;
}

class PremiumUser implements User {
  constructor(public totalPurchases: number) {}

  calculateDiscount(): number {
    return this.totalPurchases * 0.2;
  }
}

class RegularUser implements User {
  constructor(public totalPurchases: number) {}

  calculateDiscount(): number {
    return this.totalPurchases * 0.1;
  }
}

class GuestUser implements User {
  calculateDiscount(): number {
    return 0;
  }
}

// Usage
const discount = user.calculateDiscount();  // No conditional needed
```

**Benefits:**
- Open/Closed Principle (open for extension, closed for modification)
- Adding new types doesn't require changing existing code
- Cleaner code

---

## Extract Method

**When to use:**
- A method is too long
- Code has duplicated logic
- Part of a method can be reused elsewhere

**Steps:**
1. Identify cohesive block of code
2. Extract it to a new method with a descriptive name
3. Replace original code with method call

**Example:**

Before:
```typescript
function processOrder(order: Order) {
  // Validate order
  if (!order.items || order.items.length === 0) {
    throw new Error("Order must have items");
  }
  if (order.total < 0) {
    throw new Error("Total cannot be negative");
  }

  // Calculate tax
  const taxRate = 0.08;
  const tax = order.total * taxRate;

  // Calculate shipping
  let shipping = 0;
  if (order.total < 50) {
    shipping = 10;
  }

  // Save to DB
  db.save({ ...order, tax, shipping });
}
```

After:
```typescript
function processOrder(order: Order) {
  validateOrder(order);
  const tax = calculateTax(order.total);
  const shipping = calculateShipping(order.total);
  saveOrder(order, tax, shipping);
}

function validateOrder(order: Order) {
  if (!order.items || order.items.length === 0) {
    throw new Error("Order must have items");
  }
  if (order.total < 0) {
    throw new Error("Total cannot be negative");
  }
}

function calculateTax(total: number): number {
  const taxRate = 0.08;
  return total * taxRate;
}

function calculateShipping(total: number): number {
  return total < 50 ? 10 : 0;
}

function saveOrder(order: Order, tax: number, shipping: number) {
  db.save({ ...order, tax, shipping });
}
```

**Benefits:**
- Each method has a clear, single purpose
- Easier to test
- Reusable logic

---

## Introduce Parameter Object

**When to use:**
- A method has too many parameters (>3-4)
- The same group of parameters appears in multiple methods

**Steps:**
1. Create a class or interface to hold related parameters
2. Replace individual parameters with the new object
3. Update callers to pass the object

**Example:**

Before:
```typescript
function createUser(
  name: string,
  email: string,
  street: string,
  city: string,
  zipCode: string,
  country: string
) {
  // ...
}

createUser("Alice", "alice@example.com", "123 Main St", "NYC", "10001", "USA");
```

After:
```typescript
interface Address {
  street: string;
  city: string;
  zipCode: string;
  country: string;
}

interface CreateUserParams {
  name: string;
  email: string;
  address: Address;
}

function createUser(params: CreateUserParams) {
  // ...
}

createUser({
  name: "Alice",
  email: "alice@example.com",
  address: {
    street: "123 Main St",
    city: "NYC",
    zipCode: "10001",
    country: "USA"
  }
});
```

**Benefits:**
- Clearer method signatures
- Easier to add new fields
- Type-safe

---

## Strangler Fig Pattern

**When to use:**
- You need to migrate from a legacy system gradually
- The system is too large to refactor all at once
- You want to minimize risk during migration

**Steps:**
1. Create new implementation alongside old one
2. Gradually route traffic to new implementation
3. Monitor and validate new implementation
4. Once fully migrated, remove old implementation

**Example:**

Phase 1: Both old and new implementations coexist

```typescript
// Old implementation (legacy)
function legacyCalculatePrice(items: Item[]): number {
  // Complex legacy logic...
}

// New implementation
function calculatePrice(items: Item[]): number {
  // Clean, tested logic...
}

// Router (feature flag)
function getPrice(items: Item[]): number {
  if (process.env.USE_NEW_PRICING === "true") {
    return calculatePrice(items);
  } else {
    return legacyCalculatePrice(items);
  }
}
```

Phase 2: Gradual rollout (10% → 50% → 100%)

```typescript
function getPrice(items: Item[]): number {
  const rolloutPercentage = 50;  // Gradually increase

  if (Math.random() * 100 < rolloutPercentage) {
    return calculatePrice(items);  // New
  } else {
    return legacyCalculatePrice(items);  // Old
  }
}
```

Phase 3: Full migration, remove old code

```typescript
function getPrice(items: Item[]): number {
  return calculatePrice(items);  // Only new implementation remains
}

// legacyCalculatePrice() is deleted
```

**Benefits:**
- Low-risk migration
- Can roll back easily
- Validate new implementation in production

---

## Additional Resources

- **Martin Fowler's Refactoring Catalog**: https://refactoring.com/catalog/
- **Refactoring Guru**: https://refactoring.guru/refactoring/techniques
- **Clean Code by Robert C. Martin**: Principles for writing maintainable code

---

**Last Updated:** 2026-02-15
**Maintained by:** AI-SDD plan-refactor skill
