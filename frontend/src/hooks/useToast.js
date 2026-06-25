/**
 * useToast.js — Convenience hook for the toast system.
 */
import { useApp } from '../context/AppContext'

export const useToast = () => {
  const { toast } = useApp()
  return toast
}
