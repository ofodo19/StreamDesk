plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }

android {
    namespace = "com.vertextech.streamdesk"
    compileSdk = 35
    defaultConfig { applicationId = "com.vertextech.streamdesk"; minSdk = 23; targetSdk = 35; versionCode = 1; versionName = "1.0.0" }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    // Java and Kotlin must target the same JVM version
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.media3:media3-exoplayer:1.5.1")
    implementation("androidx.media3:media3-exoplayer-hls:1.5.1")
    implementation("androidx.media3:media3-ui:1.5.1")
}
