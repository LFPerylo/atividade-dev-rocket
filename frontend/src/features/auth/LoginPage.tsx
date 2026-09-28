import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'

import { useAuth } from '@/features/auth/authContext'
import { ApiError } from '@/infrastructure/http/client'
import { Button } from '@/shared/ui/Button'
import { Field, Input } from '@/shared/ui/Field'

const loginSchema = z.object({
  email: z.email('Informe um e-mail válido'),
  senha: z.string().min(1, 'Informe a senha'),
})

type LoginValues = z.infer<typeof loginSchema>

function safeRedirect(target: string | null): string {
  return target?.startsWith('/') && !target.startsWith('//') ? target : '/'
}

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [serverError, setServerError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) })

  const onSubmit = handleSubmit(async ({ email, senha }) => {
    setServerError(null)
    try {
      await login(email, senha)
      navigate(safeRedirect(params.get('next')), { replace: true })
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : 'Não foi possível entrar')
    }
  })

  return (
    <section className="mx-auto flex max-w-sm flex-col gap-6 py-16">
      <header className="text-center">
        <h1 className="font-display text-3xl font-semibold text-ink-100">Área do administrador</h1>
        <p className="mt-2 text-sm text-ink-400">
          Entre para cadastrar filmes e registrar avaliações.
        </p>
      </header>
      <form
        onSubmit={onSubmit}
        noValidate
        className="flex flex-col gap-4 rounded-xl border border-ink-700 bg-ink-800 p-6"
      >
        <Field id="email" label="E-mail" error={errors.email?.message}>
          <Input
            id="email"
            type="email"
            autoComplete="username"
            invalid={Boolean(errors.email)}
            {...register('email')}
          />
        </Field>
        <Field id="senha" label="Senha" error={errors.senha?.message}>
          <Input
            id="senha"
            type="password"
            autoComplete="current-password"
            invalid={Boolean(errors.senha)}
            {...register('senha')}
          />
        </Field>
        {serverError && (
          <p role="alert" className="rounded-md bg-danger-500/15 px-3 py-2 text-sm text-danger-400">
            {serverError}
          </p>
        )}
        <Button type="submit" loading={isSubmitting}>
          Entrar
        </Button>
      </form>
    </section>
  )
}
