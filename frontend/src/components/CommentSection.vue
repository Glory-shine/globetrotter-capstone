<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { createComment, listComments, toggleCommentLike } from '../api/comments'
import { authStore } from '../stores/auth'
import { toastStore } from '../stores/toast'

const props = defineProps({
  destinationId: { type: String, required: true },
  highlightId: { type: String, default: null },
})

const comments = ref([])
const loading = ref(true)
const newText = ref('')
const submitting = ref(false)
const replyingTo = ref(null)
const replyText = ref('')
const replySubmitting = ref(false)

async function load() {
  loading.value = true
  try {
    comments.value = await listComments(props.destinationId)
    if (props.highlightId) {
      await nextTick()
      scrollToHighlight()
    }
  } catch {
    // interceptor already surfaced a toast
  } finally {
    loading.value = false
  }
}

function scrollToHighlight() {
  const el = document.getElementById(`comment-${props.highlightId}`)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return "à l'instant"
  if (minutes < 60) return `il y a ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `il y a ${hours} h`
  const days = Math.floor(hours / 24)
  return `il y a ${days} j`
}

async function submitComment() {
  if (!newText.value.trim()) return
  submitting.value = true
  try {
    const created = await createComment(props.destinationId, { text: newText.value.trim() })
    comments.value = [created, ...comments.value]
    newText.value = ''
  } catch {
    // interceptor already surfaced a toast
  } finally {
    submitting.value = false
  }
}

function openReply(commentId) {
  replyingTo.value = replyingTo.value === commentId ? null : commentId
  replyText.value = ''
}

async function submitReply(parentComment) {
  if (!replyText.value.trim()) return
  replySubmitting.value = true
  try {
    const created = await createComment(props.destinationId, {
      text: replyText.value.trim(),
      parentId: parentComment.id,
    })
    parentComment.replies.push(created)
    replyText.value = ''
    replyingTo.value = null
  } catch {
    // interceptor already surfaced a toast
  } finally {
    replySubmitting.value = false
  }
}

async function like(comment) {
  try {
    const updated = await toggleCommentLike(comment.id)
    comment.likes_count = updated.likes_count
    comment.liked_by_me = updated.liked_by_me
  } catch {
    toastStore.error("Impossible d'enregistrer votre réaction pour le moment.")
  }
}

function initial(username) {
  return (username || '?').charAt(0).toUpperCase()
}

onMounted(load)
</script>

<template>
  <div class="rounded-2xl border border-border-light bg-white p-5 sm:p-6">
    <h2 class="font-display text-lg font-semibold text-deep-blue">Avis & commentaires</h2>
    <p class="mt-1 text-xs text-text-secondary">Partagez votre expérience, ou répondez à un avis.</p>

    <form class="mt-4 flex gap-2" @submit.prevent="submitComment">
      <div class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-sage/15 text-sm font-semibold text-sage">
        {{ initial(authStore.state.username) }}
      </div>
      <div class="flex-1">
        <textarea
          v-model="newText"
          rows="2"
          placeholder="Votre avis sur ce lieu…"
          class="w-full resize-none rounded-xl border border-border-light bg-cream/60 px-3 py-2 text-sm text-text-primary outline-none focus:border-sage focus:ring-2 focus:ring-sage/20"
        />
        <div class="mt-2 flex justify-end">
          <button
            type="submit"
            :disabled="submitting || !newText.trim()"
            class="rounded-full bg-sage px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-sage-light disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ submitting ? 'Publication…' : 'Publier' }}
          </button>
        </div>
      </div>
    </form>

    <div v-if="loading" class="mt-6 animate-pulse space-y-3">
      <div class="h-16 rounded-xl bg-cream-dark" />
      <div class="h-16 rounded-xl bg-cream-dark" />
    </div>

    <div v-else-if="comments.length" class="mt-6 space-y-5">
      <div
        v-for="comment in comments"
        :key="comment.id"
        :id="`comment-${comment.id}`"
        class="border-t border-border-light pt-5 first:border-t-0 first:pt-0 transition-colors duration-500"
        :class="{ 'rounded-xl bg-sage/10 ring-2 ring-sage/40': highlightId === comment.id }"
      >
        <div class="flex gap-3">
          <div class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-lavender-light text-sm font-semibold text-lavender">
            {{ initial(comment.username) }}
          </div>
          <div class="flex-1">
            <div class="flex items-baseline gap-2">
              <span class="text-sm font-semibold text-deep-blue">{{ comment.username }}</span>
              <span class="text-xs text-text-light">{{ timeAgo(comment.created_at) }}</span>
            </div>
            <p class="mt-1 text-sm leading-relaxed text-text-primary">{{ comment.text }}</p>

            <div class="mt-2 flex items-center gap-4">
              <button
                type="button"
                class="flex items-center gap-1 text-xs font-medium transition"
                :class="comment.liked_by_me ? 'text-sage' : 'text-text-secondary hover:text-sage'"
                @click="like(comment)"
              >
                <span>{{ comment.liked_by_me ? '♥' : '♡' }}</span>
                {{ comment.likes_count || '' }}
              </button>
              <button
                type="button"
                class="text-xs font-medium text-text-secondary hover:text-sage"
                @click="openReply(comment.id)"
              >
                Répondre
              </button>
            </div>

            <form v-if="replyingTo === comment.id" class="mt-3 flex gap-2" @submit.prevent="submitReply(comment)">
              <textarea
                v-model="replyText"
                rows="2"
                :placeholder="`Répondre à ${comment.username}…`"
                class="flex-1 resize-none rounded-xl border border-border-light bg-cream/60 px-3 py-2 text-xs text-text-primary outline-none focus:border-sage focus:ring-2 focus:ring-sage/20"
              />
              <button
                type="submit"
                :disabled="replySubmitting || !replyText.trim()"
                class="self-start rounded-full bg-deep-blue px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-sage disabled:cursor-not-allowed disabled:opacity-50"
              >
                Envoyer
              </button>
            </form>

            <div v-if="comment.replies?.length" class="mt-4 space-y-4 border-l-2 border-border-light pl-4">
              <div v-for="reply in comment.replies" :key="reply.id" :id="`comment-${reply.id}`" class="flex gap-2 rounded-lg transition-colors duration-500" :class="{ 'bg-sage/10 ring-2 ring-sage/40 p-2': highlightId === reply.id }">
                <div class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-cream-dark text-xs font-semibold text-deep-blue">
                  {{ initial(reply.username) }}
                </div>
                <div>
                  <div class="flex items-baseline gap-2">
                    <span class="text-xs font-semibold text-deep-blue">{{ reply.username }}</span>
                    <span class="text-[11px] text-text-light">{{ timeAgo(reply.created_at) }}</span>
                  </div>
                  <p class="mt-0.5 text-xs leading-relaxed text-text-primary">{{ reply.text }}</p>
                  <button
                    type="button"
                    class="mt-1 flex items-center gap-1 text-[11px] font-medium transition"
                    :class="reply.liked_by_me ? 'text-sage' : 'text-text-secondary hover:text-sage'"
                    @click="like(reply)"
                  >
                    <span>{{ reply.liked_by_me ? '♥' : '♡' }}</span>
                    {{ reply.likes_count || '' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <p v-else class="mt-6 text-sm text-text-secondary">
      Aucun avis pour l'instant — soyez le premier à partager votre expérience !
    </p>
  </div>
</template>
