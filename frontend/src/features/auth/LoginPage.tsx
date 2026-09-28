import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '@/features/auth/AuthLayout'
import { useAuth } from '@/features/auth/authContext'
import { safeRedirect, withNext } from '@/features/auth/redirect'
import { ApiError } from '@/infrastructure/http/client'
import { Button } from '@/shared/ui/Button'
import { Field, Input } from '@/shared/ui/Field'

const loginSchema = z.object({
  email: z.email('Informe um e-mail válido'),
  senha: z.string().min(1, 'Informe a senha'),
})

type LoginValues = z.infer<typeof loginSchema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const next = params.get('next')
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
      navigate(safeRedirect(next), { replace: true })
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : 'Não foi possível entrar')
    }
  })

  return (
    <AuthLayout
      title="Entrar"
      description="Acesse sua conta para avaliar filmes."
      footer={
        <>
          Ainda não tem conta?{' '}
          <Link
            to={withNext('/cadastro', next)}
            className="font-semibold text-accent-400 hover:underline"
          >
            Criar conta
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
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
    </AuthLayout>
  )
}
