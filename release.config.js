module.exports = {
    branches: [
        'main',
        { name: 'Dev', prerelease: 'dev' },
    ],
    plugins: [
        ['@semantic-release/commit-analyzer', { preset: 'conventionalcommits' }],
        ['@semantic-release/release-notes-generator', { preset: 'conventionalcommits' }],
        ['@semantic-release/changelog', { changelogFile: 'CHANGELOG.md' }],
        // Atualiza apenas o version do frontend; não publica no npm
        ['@semantic-release/npm', { npmPublish: false, pkgRoot: 'FrontEnd' }],
        ['@semantic-release/github', { assets: [] }],
        ['@semantic-release/git', {
            assets: ['CHANGELOG.md', 'FrontEnd/package.json'],
            message: 'chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}'
        }],
    ],
};
