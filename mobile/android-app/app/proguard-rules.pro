# Retrofit
-keepattributes Signature
-keepattributes Exceptions
-keep class com.faceshield.mobile.model.** { *; }
-keep class com.faceshield.mobile.network.** { *; }

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**

# Gson
-keepattributes *Annotation*
-keep class com.google.gson.** { *; }

# Kotlin Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Compose Animation — prevent R8 from removing keyframes API methods
-keep class androidx.compose.animation.core.KeyframesSpec { *; }
-keep class androidx.compose.animation.core.KeyframesSpec$KeyframesSpecConfig { *; }
-keep class androidx.compose.animation.core.KeyframesSpec$KeyframeEntity { *; }
-dontoptimize