import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'

import { useAuth } from '@/features/auth/authContext'
import { safeRedirect, withNext } from '@/features/auth/redirect'
import { ApiError } from '@/infrastructure/http/client'
import { Button } from '@/shared/ui/Button'
import { Field, Input } from '@/shared/ui/Field'

const MIN_PASSWORD_LENGTH = 8

const registerSchema = z
  .object({
    nome: z.string().trim().min(1, 'Informe seu nome').max(120, 'Máximo de 120 caracteres'),
    email: z.email('Informe um e-mail válido'),
    senha: z.string().min(MIN_PASSWORD_LENGTH, `Use ao menos ${MIN_PASSWORD_LENGTH} caracteres`),
    confirmar: z.string(),
  })
  .refine(({ senha, confirmar }) => senha === confirmar, {
    path: ['confirmar'],
    message: 'As senhas não conferem',
  })

type RegisterValues = z.infer<typeof registerSchema>

export function RegisterPage() {
  const { register: createAccount } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const next = params.get('next')
  const [serverError, setServerError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) })

  const onSubmit = handleSubmit(async ({ nome, email, senha }) => {
    setServerError(null)
    try {
      await createAccount({ nome: nome.trim(), email, senha })
      navigate(safeRedirect(next), { replace: true })
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : 'Não foi possível criar a conta')
    }
  })

  return (
    <section className="mx-auto flex max-w-sm flex-col gap-6 py-16">
      <header className="text-center">
        <h1 className="font-display text-3xl font-semibold text-ink-100">Crie sua conta</h1>
        <p className="mt-2 text-sm text-ink-400">
          Avalie os filmes que você viu e acompanhe as notas.
        </p>
      </header>
      <form
        onSubmit={onSubmit}
        noValidate
        className="flex flex-col gap-4 rounded-xl border border-ink-700 bg-ink-800 p-6"
      >
        <Field id="nome" label="Nome" error={errors.nome?.message}>
          <Input
            id="nome"
            autoComplete="name"
            invalid={Boolean(errors.nome)}
            {...register('nome')}
          />
        </Field>
        <Field id="email" label="E-mail" error={errors.email?.message}>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            invalid={Boolean(errors.email)}
            {...register('email')}
          />
        </Field>
        <Field id="senha" label="Senha" error={errors.senha?.message}>
          <Input
            id="senha"
            type="password"
            autoComplete="new-password"
            invalid={Boolean(errors.senha)}
            {...register('senha')}
          />
        </Field>
        <Field id="confirmar" label="Confirme a senha" error={errors.confirmar?.message}>
          <Input
            id="confirmar"
            type="password"
            autoComplete="new-password"
            invalid={Boolean(errors.confirmar)}
            {...register('confirmar')}
          />
        </Field>
        {serverError && (
          <p role="alert" className="rounded-md bg-danger-500/15 px-3 py-2 text-sm text-danger-400">
            {serverError}
          </p>
        )}
        <Button type="submit" loading={isSubmitting}>
          Criar conta
        </Button>
      </form>
      <p className="text-center text-sm text-ink-400">
        Já tem conta?{' '}
        <Link
          to={withNext('/login', next)}
          className="font-semibold text-accent-400 hover:underline"
        >
          Entrar
        </Link>
      </p>
    </section>
  )
}
