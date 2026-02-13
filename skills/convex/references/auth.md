# Convex Auth Reference

Comprehensive guide to implementing authentication with Convex Auth, including OAuth providers, email authentication, password flows, session management, and function security.

## What is Convex Auth?

Convex Auth is a library enabling authentication directly within your Convex backend, eliminating the need for separate auth services or hosting servers.

**Key Benefits**:
- No separate authentication service required
- No hosting server needed
- Integrated with Convex functions and real-time subscriptions
- TypeScript-first with automatic type generation
- Multiple authentication methods supported

**Status**: Currently in beta - feedback encouraged via Discord community.

## Supported Applications

Convex Auth works with:
- **React SPAs** hosted on CDNs (Netlify, Vercel, etc.)
- **Full-stack Next.js** applications (App Router and Pages Router)
- **React Native** mobile apps (iOS and Android)

## Authentication Methods

### 1. Email-Based Authentication

Two approaches for passwordless email authentication:

**Magic Links**:
- User enters email
- Receives link via email
- Clicks link to authenticate
- No password required

**One-Time Passwords (OTPs)**:
- User enters email
- Receives numeric code via email
- Enters code to authenticate
- Short-lived code for security

### 2. OAuth Providers

Integrate with popular OAuth providers:
- **GitHub**
- **Google**
- **Apple**
- Custom OAuth providers (extensible)

### 3. Password Authentication

Traditional username/password flows:
- Password creation with validation
- Secure password storage (hashed)
- Password reset flows
- Optional email verification

## Setup and Configuration

### Installation

```bash
pnpm add @convex-dev/auth
```

### Basic Configuration

Create `convex/auth.config.ts`:

```typescript
import { convexAuth } from "@convex-dev/auth";
import GitHub from "@auth/core/providers/github";
import Google from "@auth/core/providers/google";
import { Password } from "@convex-dev/auth/providers/Password";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    Password,
  ],
});
```

### Environment Variables

Add provider credentials to `.env.local`:

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Convex Auth Secret
CONVEX_AUTH_SECRET=your_random_secret_key
```

Generate auth secret:
```bash
openssl rand -base64 32
```

### HTTP Routes

Define auth routes in `convex/http.ts`:

```typescript
import { httpRouter } from "convex/server";
import { auth } from "./auth.config";

const http = httpRouter();

// Auth routes
auth.addHttpRoutes(http);

export default http;
```

## OAuth Implementation

### GitHub Provider

**Setup Steps**:
1. Create OAuth app in GitHub Developer Settings
2. Set callback URL: `https://your-app.convex.site/api/auth/callback/github`
3. Add client ID and secret to environment variables
4. Configure provider in `auth.config.ts`

**Client-Side Sign In** (React):
```typescript
import { useAuthActions } from "@convex-dev/auth/react";

function SignInWithGitHub() {
  const { signIn } = useAuthActions();

  return (
    <button onClick={() => signIn("github")}>
      Sign in with GitHub
    </button>
  );
}
```

### Google Provider

**Setup Steps**:
1. Create OAuth 2.0 Client in Google Cloud Console
2. Set authorized redirect URI: `https://your-app.convex.site/api/auth/callback/google`
3. Add client ID and secret to environment variables
4. Configure provider in `auth.config.ts`

**Client-Side Sign In** (React):
```typescript
function SignInWithGoogle() {
  const { signIn } = useAuthActions();

  return (
    <button onClick={() => signIn("google")}>
      Sign in with Google
    </button>
  );
}
```

### Custom OAuth Provider

Extend with custom providers:

```typescript
import { OAuth } from "@convex-dev/auth/providers/OAuth";

const CustomProvider = OAuth({
  id: "custom",
  name: "Custom Provider",
  authorization: {
    url: "https://provider.com/oauth/authorize",
    params: {
      scope: "openid profile email",
      response_type: "code",
    },
  },
  token: "https://provider.com/oauth/token",
  userinfo: "https://provider.com/oauth/userinfo",
  profile(profile) {
    return {
      id: profile.sub,
      name: profile.name,
      email: profile.email,
    };
  },
});
```

## Email Authentication

### Magic Links

**Configuration**:
```typescript
import { MagicLink } from "@convex-dev/auth/providers/MagicLink";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    MagicLink({
      sendMagicLink: async ({ email, url }) => {
        // Send email with magic link URL
        await sendEmail({
          to: email,
          subject: "Sign in to your account",
          body: `Click here to sign in: ${url}`,
        });
      },
    }),
  ],
});
```

**Client-Side Usage**:
```typescript
function MagicLinkForm() {
  const { signIn } = useAuthActions();
  const [email, setEmail] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await signIn("magic-link", { email });
    alert("Check your email for the magic link!");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
      />
      <button type="submit">Send Magic Link</button>
    </form>
  );
}
```

### One-Time Passwords (OTPs)

**Configuration**:
```typescript
import { OTP } from "@convex-dev/auth/providers/OTP";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    OTP({
      sendOTP: async ({ email, code }) => {
        // Send email with OTP code
        await sendEmail({
          to: email,
          subject: "Your verification code",
          body: `Your code is: ${code}`,
        });
      },
      codeLength: 6,
      expirationMinutes: 10,
    }),
  ],
});
```

**Client-Side Usage**:
```typescript
function OTPForm() {
  const { signIn } = useAuthActions();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"email" | "code">("email");

  const handleSendCode = async () => {
    await signIn("otp", { email, flow: "send" });
    setStep("code");
  };

  const handleVerifyCode = async () => {
    await signIn("otp", { email, code, flow: "verify" });
  };

  if (step === "email") {
    return (
      <div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
        />
        <button onClick={handleSendCode}>Send Code</button>
      </div>
    );
  }

  return (
    <div>
      <input
        type="text"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Enter code"
      />
      <button onClick={handleVerifyCode}>Verify</button>
    </div>
  );
}
```

## Password Authentication

### Setup

**Configuration**:
```typescript
import { Password } from "@convex-dev/auth/providers/Password";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [
    Password({
      // Optional: Add email verification
      verify: async ({ email, token }) => {
        await sendEmail({
          to: email,
          subject: "Verify your email",
          body: `Verification link: ${token}`,
        });
      },
    }),
  ],
});
```

### Sign Up

**Client-Side**:
```typescript
function SignUpForm() {
  const { signIn } = useAuthActions();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signIn("password", {
        email,
        password,
        flow: "signUp",
      });
    } catch (error) {
      console.error("Sign up failed:", error);
    }
  };

  return (
    <form onSubmit={handleSignUp}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
        minLength={8}
      />
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

### Sign In

**Client-Side**:
```typescript
function SignInForm() {
  const { signIn } = useAuthActions();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signIn("password", {
        email,
        password,
        flow: "signIn",
      });
    } catch (error) {
      console.error("Sign in failed:", error);
    }
  };

  return (
    <form onSubmit={handleSignIn}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Sign In</button>
    </form>
  );
}
```

### Password Reset

**Configuration with Reset Handler**:
```typescript
Password({
  reset: async ({ email, token }) => {
    await sendEmail({
      to: email,
      subject: "Reset your password",
      body: `Reset link: https://your-app.com/reset?token=${token}`,
    });
  },
})
```

**Client-Side Flow**:
```typescript
function PasswordResetFlow() {
  const { signIn } = useAuthActions();
  const [step, setStep] = useState<"request" | "reset">("request");
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const handleRequestReset = async () => {
    await signIn("password", {
      email,
      flow: "reset-request",
    });
    setStep("reset");
  };

  const handleResetPassword = async () => {
    await signIn("password", {
      email,
      token,
      newPassword,
      flow: "reset-confirm",
    });
  };

  if (step === "request") {
    return (
      <div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
        <button onClick={handleRequestReset}>Request Reset</button>
      </div>
    );
  }

  return (
    <div>
      <input
        type="text"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        placeholder="Reset token"
      />
      <input
        type="password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        placeholder="New password"
      />
      <button onClick={handleResetPassword}>Reset Password</button>
    </div>
  );
}
```

## Session Management

### Getting Current User

**In Queries/Mutations**:
```typescript
import { query } from "./_generated/server";
import { auth } from "./auth.config";

export const getCurrentUser = query({
  args: {},
  returns: v.union(v.null(), v.object({
    _id: v.id("users"),
    email: v.string(),
    name: v.optional(v.string()),
  })),
  handler: async (ctx) => {
    const userId = await auth.getUserId(ctx);
    if (!userId) {
      return null;
    }

    const user = await ctx.db.get(userId);
    return user;
  },
});
```

**In React Components**:
```typescript
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

function ProfilePage() {
  const user = useQuery(api.users.getCurrentUser);

  if (!user) {
    return <div>Please sign in</div>;
  }

  return <div>Welcome, {user.name || user.email}!</div>;
}
```

### Sign Out

**Client-Side**:
```typescript
function SignOutButton() {
  const { signOut } = useAuthActions();

  return <button onClick={() => signOut()}>Sign Out</button>;
}
```

## Securing Functions

### Require Authentication

**Pattern 1: Explicit Check**:
```typescript
import { mutation } from "./_generated/server";
import { auth } from "./auth.config";
import { v } from "convex/values";

export const createPost = mutation({
  args: { title: v.string(), content: v.string() },
  returns: v.id("posts"),
  handler: async (ctx, args) => {
    const userId = await auth.getUserId(ctx);
    if (!userId) {
      throw new Error("Not authenticated");
    }

    return await ctx.db.insert("posts", {
      ...args,
      authorId: userId,
      createdAt: Date.now(),
    });
  },
});
```

**Pattern 2: Helper Function**:
```typescript
async function requireAuth(ctx: QueryCtx | MutationCtx) {
  const userId = await auth.getUserId(ctx);
  if (!userId) {
    throw new Error("Authentication required");
  }
  return userId;
}

export const createPost = mutation({
  args: { title: v.string(), content: v.string() },
  returns: v.id("posts"),
  handler: async (ctx, args) => {
    const userId = await requireAuth(ctx);

    return await ctx.db.insert("posts", {
      ...args,
      authorId: userId,
      createdAt: Date.now(),
    });
  },
});
```

### Authorization Patterns

**Resource Ownership Check**:
```typescript
export const updatePost = mutation({
  args: {
    postId: v.id("posts"),
    title: v.string(),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const userId = await requireAuth(ctx);

    const post = await ctx.db.get(args.postId);
    if (!post) {
      throw new Error("Post not found");
    }

    if (post.authorId !== userId) {
      throw new Error("Not authorized to update this post");
    }

    await ctx.db.patch(args.postId, {
      title: args.title,
      content: args.content,
    });

    return null;
  },
});
```

**Role-Based Access Control**:
```typescript
async function requireRole(ctx: QueryCtx | MutationCtx, role: "admin" | "moderator") {
  const userId = await requireAuth(ctx);

  const user = await ctx.db.get(userId);
  if (!user?.role || user.role !== role) {
    throw new Error(`Requires ${role} role`);
  }

  return userId;
}

export const deleteAnyPost = mutation({
  args: { postId: v.id("posts") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await requireRole(ctx, "admin");

    await ctx.db.delete(args.postId);
    return null;
  },
});
```

## User Management

### User Schema

Define user table in `convex/schema.ts`:

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";
import { authTables } from "@convex-dev/auth/server";

export default defineSchema({
  ...authTables,
  users: defineTable({
    email: v.string(),
    name: v.optional(v.string()),
    role: v.optional(v.union(v.literal("admin"), v.literal("user"))),
    createdAt: v.number(),
  }).index("by_email", ["email"]),
});
```

### Update User Profile

```typescript
export const updateProfile = mutation({
  args: {
    name: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const userId = await requireAuth(ctx);

    await ctx.db.patch(userId, {
      name: args.name,
    });

    return null;
  },
});
```

### List Users (Admin Only)

```typescript
export const listUsers = query({
  args: {},
  returns: v.array(v.object({
    _id: v.id("users"),
    email: v.string(),
    name: v.optional(v.string()),
    createdAt: v.number(),
  })),
  handler: async (ctx) => {
    await requireRole(ctx, "admin");

    return await ctx.db.query("users").collect();
  },
});
```

## React Native Integration

### Setup

Install dependencies:
```bash
pnpm add @convex-dev/auth @auth/core react-native-webview
```

### Configuration

Wrap app with auth provider:

```typescript
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { ConvexAuthProvider } from "@convex-dev/auth/react";

const convex = new ConvexReactClient(process.env.CONVEX_URL!);

export default function App() {
  return (
    <ConvexProvider client={convex}>
      <ConvexAuthProvider>
        <MainApp />
      </ConvexAuthProvider>
    </ConvexProvider>
  );
}
```

### Sign In Component

```typescript
import { useAuthActions } from "@convex-dev/auth/react";
import { View, TextInput, Button } from "react-native";
import { useState } from "react";

function SignIn() {
  const { signIn } = useAuthActions();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignIn = async () => {
    try {
      await signIn("password", { email, password, flow: "signIn" });
    } catch (error) {
      console.error("Sign in failed:", error);
    }
  };

  return (
    <View>
      <TextInput
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        keyboardType="email-address"
      />
      <TextInput
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
      />
      <Button title="Sign In" onPress={handleSignIn} />
    </View>
  );
}
```

## Best Practices

1. **Secure Secrets**: Store OAuth credentials and auth secrets in environment variables
2. **Validate Inputs**: Always validate email formats and password strength
3. **Use HTTPS**: Ensure production apps use HTTPS for auth callbacks
4. **Implement Rate Limiting**: Prevent brute force attacks on password endpoints
5. **Add Email Verification**: Verify email ownership before granting full access
6. **Use Strong Passwords**: Enforce minimum length and complexity requirements
7. **Handle Errors Gracefully**: Provide clear error messages without leaking security info
8. **Implement Session Timeouts**: Automatically expire sessions after inactivity
9. **Log Auth Events**: Track sign-ins, sign-outs, and failed attempts for security monitoring
10. **Test All Flows**: Verify sign up, sign in, password reset, and OAuth flows work correctly

## Common Patterns

### Protected Routes (React)

```typescript
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
import { Navigate } from "react-router-dom";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useQuery(api.users.getCurrentUser);

  if (user === undefined) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/sign-in" />;
  }

  return <>{children}</>;
}
```

### Multi-Provider Sign In

```typescript
function SignInOptions() {
  const { signIn } = useAuthActions();

  return (
    <div>
      <button onClick={() => signIn("github")}>
        Sign in with GitHub
      </button>
      <button onClick={() => signIn("google")}>
        Sign in with Google
      </button>
      <hr />
      <PasswordSignInForm />
    </div>
  );
}
```

### Account Linking

Allow users to link multiple providers:

```typescript
export const linkProvider = mutation({
  args: { provider: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    const userId = await requireAuth(ctx);

    // Store pending link request
    await ctx.db.insert("pendingLinks", {
      userId,
      provider: args.provider,
      expiresAt: Date.now() + 600000, // 10 minutes
    });

    return null;
  },
});
```

## Troubleshooting

**Common Issues**:

1. **OAuth Callback Errors**: Verify redirect URIs match exactly in provider settings
2. **Session Not Persisting**: Check cookie settings and HTTPS configuration
3. **Email Not Sending**: Verify email service configuration and API keys
4. **TypeScript Errors**: Run `pnpm convex dev` to regenerate types after schema changes
5. **Auth State Not Updating**: Ensure ConvexAuthProvider wraps components using auth

**Debug Logging**:
```typescript
export const debugAuth = query({
  args: {},
  returns: v.object({
    isAuthenticated: v.boolean(),
    userId: v.optional(v.id("users")),
  }),
  handler: async (ctx) => {
    const userId = await auth.getUserId(ctx);
    return {
      isAuthenticated: !!userId,
      userId: userId || undefined,
    };
  },
});
```
